# -*- coding: UTF-8 -*-
"""
This is the MIT license: http://www.opensource.org/licenses/mit-license.php

Copyright (c) 2017 by Konstantin Lebedev.

Copyright 2022- 2023 Bytedance Ltd. and/or its affiliates

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json, base64
from distutils.core import extension_keywords

from django.db import transaction

from salt.models import host_group, host_group_minion, salt_master, task_list, shell_template, user_relationship, \
    resource_group, rg_relationship, User, transfer_file
from ansible.common.an_api import AnsibleAPI
import logging, traceback, time, random
from django.conf import settings
import datetime, os

logger = logging.getLogger("default")

def exec_remote_shell(*args, **kwargs):
    """
    执行shell和playbook任务
    :param args:
    :param kwargs:
    :return:
    """
    host_group_id, encap_exec_content, current_user = args

    count_success = count_fail = 0
    exec_remote_shell_result_filename = str(current_user) + "-" + ''.join(random.choices('0123456789', k=9)) + time.strftime(
        "%Y%m%d%H%M%S", time.localtime()) + '.txt'
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())

    # confirm that exec_content is command(1) or template(0)
    encap_exec_content = json.loads(encap_exec_content)
    if encap_exec_content["type"] == 1:
        exec_content = base64.b64decode(encap_exec_content["content"]).decode() #input shell
    elif encap_exec_content["type"] == 0:
        current_st = shell_template.objects.get(id=encap_exec_content["content"])
        if current_st.type == 2:
            correct_result = correct_file(host_group_id, encap_exec_content["content"])
            if correct_result["status"] == 0:
                exec_content = correct_result["playbook_name"] # playbook
            else:
                logger.error(correct_result["msg"])
                return {"count_success": count_success, "count_fail": count_fail,
                        "exec_remote_shell_result_filename": exec_remote_shell_result_filename}
        else:
            exec_content = current_st.main_content # shell template

    # get all for current user who owned
    current_user_salt = []
    current_user_salt_object = []
    current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=current_user)).values("rg")
    for each_user_rg in current_user_rgs:
        rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
        for each_rg_salt in rg_salt:
            current_user_salt.append(each_rg_salt["salt"])
    for each_user_salt in set(current_user_salt):
        current_user_salt_object.append(salt_master.objects.get(id=each_user_salt).id)

    try:
        an_master_id = host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()["salt_name"]
        an_master_name = salt_master.objects.get(id=an_master_id).name
        cleaned_content = ""

        if host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()["salt_name"] in current_user_salt_object:

            if encap_exec_content["type"] == 0 and shell_template.objects.get(
                    id=encap_exec_content["content"]).type == 2:
                correct_result = correct_file(host_group_id, encap_exec_content["content"])
                an_instance = AnsibleAPI(correct_result["private_data_dir"], correct_result["login_key"])
                run_result = an_instance.run_playbook(correct_result["playbook_name"])
            else:
                correct_result = correct_file(host_group_id=host_group_id)
                an_instance = AnsibleAPI(correct_result["private_data_dir"], correct_result["login_key"])
                run_result = an_instance.run_command(module='command', arg=exec_content)

            if an_instance.last_event.get("event_data", None):
                count_success = len(an_instance.last_event["event_data"]["ok"])
                count_fail = len(an_instance.last_event["event_data"]["processed"]) - count_success
            with open(run_result.config.artifact_dir+'/stdout', 'r') as rrcad:
                each_line = rrcad.readline()
                while each_line:
                    cleaned_content = cleaned_content+each_line
                    each_line = rrcad.readline()

        else:
            cleaned_content = "no permission to do this operation"

        with open(settings.DOWNLOAD_ROOT + exec_remote_shell_result_filename, 'a+', encoding="utf-8") as ersrfa:
                ersrfa.write(f"{an_master_name}:\n{cleaned_content}\n")

    except Exception as e:
        logger.error(traceback.format_exc())

    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_remote_shell_result_filename}

def correct_file(host_group_id, template_id=-1):
    """
    放置所有hosts & playbook文件到local
    :param template_id:
    :param host_group_id:
    :return:
    """
    if template_id == -1:
        pb_content = ""
        pb_name = ''.join(random.choices('0123456789', k=9)) + time.strftime("%Y%m%d%H%M%S", time.localtime())
    else:
        st_info = shell_template.objects.get(id=template_id)
        pb_content = st_info.main_content
        pb_name = st_info.file_name
    correct_result = {"status": 0, "msg": "ok"}

    try:
        current_an_id = list(host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id)).values("salt_name").distinct())[0]["salt_name"]
        an_base_dir = salt_master.objects.get(id=current_an_id).file_roots
        an_login_key = salt_master.objects.get(id=current_an_id).password
        an_user = salt_master.objects.get(id=current_an_id).user
        an_port = salt_master.objects.get(id=current_an_id).sftp_port
        pb_hosts_dir = os.path.join(an_base_dir, pb_name, "inventory/")
        pb_yaml_dir = os.path.join(an_base_dir, pb_name, "project/")
        an_login_key_dir = os.path.join(an_base_dir, pb_name, 'login_key')

        with transaction.atomic():
            os.makedirs(pb_yaml_dir, exist_ok=True, mode=0o755)
            os.makedirs(pb_hosts_dir, exist_ok=True, mode=0o755)

            with open(pb_hosts_dir+'hosts', "w") as phdh:
                phdh.write("[all]\n")
                for each_host in host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id)).values("minion_name"):
                    if len(each_host["minion_name"].split()) == 1:
                        each_host = each_host["minion_name"]+" ansible_port=%d ansible_user=%s" %(an_port, an_user)
                    else:
                        each_host = each_host["minion_name"]
                    phdh.write(each_host+"\n")
            with open(pb_yaml_dir+pb_name+'.yaml', "w") as pydpn:
                pydpn.write(pb_content)
            # with open(an_login_key_dir, "w") as abdpn:
            #     abdpn.write(an_login_key)
            fd = os.open(an_login_key_dir, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as abdpn:
                abdpn.write(an_login_key)

        correct_result["private_data_dir"] = an_base_dir+"/"+pb_name
        correct_result["playbook_name"] = pb_name+'.yaml'
        correct_result["login_key"] = an_base_dir+"/"+pb_name+"/"+'login_key'

    except Exception as e:
        logger.error(traceback.format_exc())
        correct_result["status"] = 1
        correct_result["msg"] = str(e)

    return correct_result

def exec_transfer_file(*args, **kwargs):
    """
    执行文件分发任务
    :param args:
    :param kwargs:
    :return:
    """
    host_group_id, transfer_file_id, current_user = args

    count_success = count_fail = 0
    exec_transfer_file_result_filename = str(current_user) + "-" + ''.join(
        random.choices('0123456789', k=9)) + time.strftime(
        "%Y%m%d%H%M%S", time.localtime()) + '.txt'
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())

    # get all for current user who owned
    current_user_salt = []
    current_user_salt_object = []
    current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=current_user)).values("rg")
    for each_user_rg in current_user_rgs:
        rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
        for each_rg_salt in rg_salt:
            current_user_salt.append(each_rg_salt["salt"])
    for each_user_salt in set(current_user_salt):
        current_user_salt_object.append(salt_master.objects.get(id=each_user_salt).id)

    # get the relevant file attr
    transfer_file_object = transfer_file.objects.get(id=transfer_file_id)
    file_name = transfer_file_object.name
    file_dest_dir = json.loads(transfer_file_object.dest_dir)
    if file_dest_dir.get("Linux", None) is None:
        cleaned_content = "only support copy files to Linux nodes"
        with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+', encoding="utf-8") as etfrf:
            etfrf.write(f"{cleaned_content}\n")
        return {"count_success": count_success, "count_fail": count_fail,
                "exec_remote_shell_result_filename": exec_transfer_file_result_filename}

    try:
        an_master_id = host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()[
            "salt_name"]
        an_master_name = salt_master.objects.get(id=an_master_id).name
        cleaned_content = ""

        if host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()["salt_name"] in current_user_salt_object:

            correct_result = correct_file(host_group_id=host_group_id)
            an_instance = AnsibleAPI(correct_result["private_data_dir"], correct_result["login_key"])
            current_an_id = list(
                host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id)).values(
                    "salt_name").distinct())[0]["salt_name"]
            an_base_dir = salt_master.objects.get(id=current_an_id).file_roots
            module_args = "src=%s dest=%s" %(os.path.join(an_base_dir, file_name), file_dest_dir.get("Linux", None))
            run_result = an_instance.transfer_file(module='copy', arg=module_args)

            count_success = len(an_instance.last_event["event_data"]["ok"])
            count_fail = len(an_instance.last_event["event_data"]["processed"]) - count_success
            with open(run_result.config.artifact_dir + '/stdout', 'r') as rrcad:
                each_line = rrcad.readline()
                while each_line:
                    cleaned_content = cleaned_content + each_line
                    each_line = rrcad.readline()

        else:
            cleaned_content = "no permission to do this operation"

        with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+', encoding="utf-8") as etfrf:
            etfrf.write(f"{an_master_name}:\n{cleaned_content}\n")

    except Exception as e:
        logger.error(traceback.format_exc())

    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_transfer_file_result_filename}