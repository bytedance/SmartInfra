# -*- coding: UTF-8 -*-
"""
// Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
"""

import json, base64
from django.db import transaction
from salt.common.notify_lark import send_lark_msg
from salt.models import host_group, host_group_minion, salt_master, task_list, shell_template, user_relationship, \
    resource_group, rg_relationship, User, transfer_file, sub_template
from ansible.common.an_api import AnsibleAPI
from salt.tasks.repeat_tasks import create_repeat_task
import logging, traceback, time, random
from django.conf import settings
import datetime, os, re, shutil

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

    if not task_list.objects.filter(id=kwargs.get("new_task_id"), status=1):
        logger.info("无有效任务信息, 定时任务停止执行")
        return
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())
    send_lark_msg(task_name=task_list.objects.get(id=kwargs.get("new_task_id")).name, current_user=current_user,
                  message="进入执行状态，请及时关注任务状态变化")

    # confirm that exec_content is command(1) or template(0)
    encap_exec_content = json.loads(encap_exec_content)
    if encap_exec_content["type"] == 1:
        exec_content = base64.b64decode(encap_exec_content["content"]).decode() #input shell
    elif encap_exec_content["type"] == 0:
        current_st = shell_template.objects.get(id=encap_exec_content["content"])
        if current_st.type == 2:
            exec_content = current_st.main_dir  # playbook
            # correct_result = correct_file(host_group_id, encap_exec_content["content"])
            # if correct_result["status"] == 0:
            #     exec_content = correct_result["playbook_name"] # playbook
            # else:
            #     logger.error(correct_result["msg"])
            #     return {"count_success": count_success, "count_fail": count_fail,
            #             "exec_remote_shell_result_filename": exec_remote_shell_result_filename}
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
        run_result = ""

        if host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()["salt_name"] in current_user_salt_object:

            if encap_exec_content["type"] == 0 and shell_template.objects.get(
                    id=encap_exec_content["content"]).type == 2:
                correct_result = correct_file(host_group_id, encap_exec_content["content"])
                an_instance = AnsibleAPI(correct_result["private_data_dir"], correct_result["login_key"])
                run_result = an_instance.run_playbook(correct_result["playbook_name"])
            else:
                correct_result = correct_file(host_group_id=host_group_id)
                an_instance = AnsibleAPI(correct_result["private_data_dir"], correct_result["login_key"])
                run_result = an_instance.run_command(module='shell', arg=exec_content)

            if an_instance.last_event.get("event_data", None):
                count_success = len(an_instance.last_event["event_data"]["ok"])
                count_fail = len(an_instance.last_event["event_data"]["processed"]) - count_success
            cleaned_content = an_instance.log_lines

        else:
            cleaned_content = ["no permission to do this operation"]

        with open(settings.DOWNLOAD_ROOT + exec_remote_shell_result_filename, 'a+', encoding="utf-8") as ersrfa:
            # record the stdout at first
            if not isinstance(run_result, str):
                for each_rr in run_result.stdout:
                    each_rr = each_rr.replace('\r', '').rstrip('\n')
                    ersrfa.write(re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', each_rr) + '\n')
            ersrfa.write("\n")
            ersrfa.write("-----------------------------------------------------------------------------------------------------------------------------\n")
            ersrfa.write("\n")
            ersrfa.write("########################## Detailed Information ##########################\n")
            ersrfa.write("\n")
            # record the detailed result
            for each_line in cleaned_content:
                each_line = each_line.replace('\r', '').rstrip('\n')
                ersrfa.write(re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', each_line) + '\n')

    except Exception as e:
        logger.error(traceback.format_exc())

    create_repeat_task(old_id=kwargs.get("new_task_id"))
    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_remote_shell_result_filename}

def resolve_path(file_path):
    """
    解析路径和文件名
    :param file_path:
    :return:
    """
    resolve_result = {"path_name": "", "file_name": ""}

    if file_path.startswith("/"):
        file_path = file_path[1:]
    if "/" in file_path:
        resolve_rule = file_path.rsplit('/', 1)
        resolve_result["path_name"] = resolve_rule[0]
        resolve_result["file_name"] = resolve_rule[1]
    else:
        resolve_result["file_name"] = file_path
        resolve_result["path_name"] = ""
    return resolve_result

def correct_file(host_group_id, template_id=-1):
    """
    放置所有hosts & playbook文件到local
    :param template_id:
    :param host_group_id:
    :return:
    """
    if template_id == -1:
        main_content = ""
        main_dir = ""
        extra_vars = ""
        pb_name = ''.join(random.choices('0123456789', k=9)) + time.strftime("%Y%m%d%H%M%S", time.localtime())
    else:
        st_info = shell_template.objects.get(id=template_id)
        main_content = st_info.main_content
        pb_name = st_info.file_name + "_" + ''.join(random.choices('0123456789', k=9))
        main_dir = st_info.main_dir
        extra_vars = st_info.extra_vars
    correct_result = {"status": 0, "msg": "ok"}

    try:
        current_an_id = list(host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id)).values("salt_name").distinct())[0]["salt_name"]
        an_base_dir = salt_master.objects.get(id=current_an_id).file_roots
        an_login_key = salt_master.objects.get(id=current_an_id).password
        an_user = salt_master.objects.get(id=current_an_id).user
        an_port = salt_master.objects.get(id=current_an_id).sftp_port
        pb_hosts_dir = os.path.join(an_base_dir, pb_name, "inventory/")
        main_pb_yaml_dir = os.path.join(an_base_dir, pb_name, "project/", resolve_path(main_dir)["path_name"])
        an_login_key_dir = os.path.join(an_base_dir, pb_name, 'login_key')
        pb_env_dir = os.path.join(an_base_dir, pb_name, "env/")
        pb_base_dir = os.path.join(an_base_dir, pb_name)

        with transaction.atomic():
            os.makedirs(main_pb_yaml_dir, exist_ok=True, mode=0o755)
            os.makedirs(pb_hosts_dir, exist_ok=True, mode=0o755)
            os.makedirs(pb_env_dir, exist_ok=True, mode=0o755)
            # record all target hosts
            with open(pb_hosts_dir+'hosts', "w") as phdh:
                phdh.write("[all]\n")
                for each_host in host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id)).values("minion_name"):
                    if len(each_host["minion_name"].split()) == 1:
                        each_host = each_host["minion_name"]+" ansible_port=%d ansible_user=%s" %(an_port, an_user)
                    else:
                        each_host = each_host["minion_name"]
                    phdh.write(each_host+"\n")
            # record all playbooks
            if template_id != -1:
                with open(main_pb_yaml_dir + "/" + resolve_path(main_dir)["file_name"], "w") as mpyd:
                    mpyd.write(main_content)
                if extra_vars:
                    with open(pb_env_dir + "extravars", "w") as ped:
                        ped.write(extra_vars)
                for each_sub_st in sub_template.objects.filter(name=shell_template.objects.get(id=template_id), history=0).values():
                    sub_pb_yaml_dir = os.path.join(an_base_dir, pb_name, "project/", resolve_path(each_sub_st["func_dir"])["path_name"])
                    os.makedirs(sub_pb_yaml_dir, exist_ok=True, mode=0o755)
                    with open(sub_pb_yaml_dir+"/"+resolve_path(each_sub_st["func_dir"])["file_name"], "w") as spyd:
                        spyd.write(each_sub_st["func_content"])
            # record private key
            fd = os.open(an_login_key_dir, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as abdpn:
                abdpn.write(an_login_key+"\n")

        correct_result["private_data_dir"] = an_base_dir+"/"+pb_name
        correct_result["playbook_name"] = main_dir
        correct_result["login_key"] = an_login_key_dir

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

    if not task_list.objects.filter(id=kwargs.get("new_task_id"), status=1):
        logger.info("无有效任务信息, 定时任务停止执行")
        return
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())
    send_lark_msg(task_name=task_list.objects.get(id=kwargs.get("new_task_id")).name, current_user=current_user,
                  message="进入执行状态，请及时关注任务状态变化")

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

        cleaned_content = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', cleaned_content)
        with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+', encoding="utf-8") as etfrf:
            etfrf.write(f"{cleaned_content}\n")

    except Exception as e:
        logger.error(traceback.format_exc())

    create_repeat_task(old_id=kwargs.get("new_task_id"))
    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_transfer_file_result_filename}