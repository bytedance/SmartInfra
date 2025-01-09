# -*- coding: UTF-8 -*-
import json, base64
from django.db import transaction

from salt.models import host_group, host_group_minion, hosts, salt_master, task_list, shell_template, user_relationship, \
    resource_group, rg_relationship, User, transfer_file
from salt.common.salt_api import SaltAPI
import logging, traceback, time, random
from django.conf import settings
import datetime, os

logger = logging.getLogger("default")

def exec_remote_shell(*args, **kwargs):
    """
    执行shell和state任务
    :param args:
    :param kwargs:
    :return:
    """
    host_group_id, encap_exec_content, current_user = args

    include_salt = []
    all_salt_ins = {}
    count_success = count_fail = 0
    exec_remote_shell_result_filename = str(current_user) + "-" + ''.join(random.choices('0123456789', k=9)) + time.strftime(
        "%Y%m%d%H%M%S", time.localtime()) + '.txt'
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())

    # confirm that exec_content is command or template
    encap_exec_content = json.loads(encap_exec_content)
    if encap_exec_content["type"] == 1:
        exec_content = base64.b64decode(encap_exec_content["content"]).decode()
    elif encap_exec_content["type"] == 0:
        current_st = shell_template.objects.get(id=encap_exec_content["content"])
        if current_st.type == 0:
            correct_result = correct_file(encap_exec_content["content"])
            if correct_result["status"] == 0:
                exec_content = current_st.file_name
            else:
                logger.error(correct_result["msg"])
                return {"count_success": count_success, "count_fail": count_fail,
                        "exec_remote_shell_result_filename": exec_remote_shell_result_filename}
        else:
            exec_content = current_st.main_content

    # get all salt for current user who owned
    current_user_salt = []
    current_user_salt_object = []
    current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=current_user)).values("rg")
    for each_user_rg in current_user_rgs:
        rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
        for each_rg_salt in rg_salt:
            current_user_salt.append(each_rg_salt["salt"])
    for each_user_salt in set(current_user_salt):
        current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))

    try:
        if host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()["salt_name"] is None:
            all_minions = host_group_minion.objects.filter(host_group_name=host_group_id).values("minion_name")
        else:
            for each_salt in host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name"):
                include_salt.append(each_salt["salt_name"])
            all_minions = hosts.objects.filter(salt__in=include_salt, status=0).values("name")

        for each_minion in all_minions:
            if each_minion.get("name", None) is None:
                each_minion = each_minion["minion_name"]
            else:
                each_minion = each_minion["name"]

            # Check whether the current user has permission to operate this node and whether the node is in the up state
            if (not hosts.objects.filter(name=each_minion, salt__in=current_user_salt_object)
                    or hosts.objects.filter(name=each_minion).values("status").first()["status"] != 0):
                count_fail += 1
                cleaned_content = "no permission or this minion status is not up"
                with open(settings.DOWNLOAD_ROOT + exec_remote_shell_result_filename, 'a+', encoding="utf-8") as ersrfa:
                    ersrfa.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')
                continue

            salt_server = salt_master.objects.get(id=hosts.objects.filter(name=each_minion).values("salt_id").first()["salt_id"])
            if salt_server.id not in all_salt_ins:
                salt_ins = SaltAPI(salt_server.host, salt_server.user, salt_server.password)
                all_salt_ins[salt_server.id] = salt_ins

            if encap_exec_content["type"] == 0 and shell_template.objects.get(id=encap_exec_content["content"]).type == 0:
                each_result = all_salt_ins[salt_server.id].execute_remote_state(each_minion, settings.STATE_HOME+exec_content)
            else:
                each_result = all_salt_ins[salt_server.id].execute_remote_shell(each_minion, exec_content)

            if each_result["status"] == 0:
                count_success += 1
                cleaned_content = str(each_result['msg'][each_minion])
            else:
                count_fail += 1
                cleaned_content = str(each_result['msg'])

            if '\\r\\n' in cleaned_content:
                cleaned_content = cleaned_content.replace('\\r\\n', '\n')
            with open(settings.DOWNLOAD_ROOT + exec_remote_shell_result_filename, 'a+', encoding="utf-8") as ersrf:
                ersrf.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')

    except Exception as e:
        logger.error(traceback.format_exc())

    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_remote_shell_result_filename}


def correct_file(template_id):
    """
    放置所有state文件到salt master
    :param template_id:
    :return:
    """
    st_info = shell_template.objects.get(id=template_id)
    main_content = st_info.main_content
    func_content = st_info.func_content
    file_name = st_info.file_name
    correct_result = {"status": 0, "msg": "ok"}

    try:
        for each_salt in salt_master.objects.all().values():
            salt_minion_name = each_salt["minion_name"]
            salt_file_roots = each_salt["file_roots"]
            if salt_file_roots[-1] != "/":
                salt_file_roots=salt_file_roots+"/"
            full_file_roots_state = salt_file_roots+settings.STATE_HOME

            base64_main_content = base64.b64encode(main_content.encode()).decode()
            base64_func_content = base64.b64encode(func_content.encode()).decode()
            salt_ins = SaltAPI(each_salt["host"], each_salt["user"], each_salt["password"])
            if main_content:
                with transaction.atomic():
                    salt_ins.execute_remote_shell(salt_minion_name, 'mkdir -p %s && echo "%s" > %s' %(
                        full_file_roots_state, base64_main_content, full_file_roots_state+file_name+'.s'))
                    salt_ins.execute_remote_shell(salt_minion_name, 'base64 --decode %s > %s' %(
                        full_file_roots_state+file_name+'.s', full_file_roots_state+file_name+'.sls'))
            if func_content:
                with transaction.atomic():
                    salt_ins.execute_remote_shell(salt_minion_name, 'echo "%s" > %s' %(
                        base64_func_content, full_file_roots_state+file_name+'.p'))
                    salt_ins.execute_remote_shell(salt_minion_name, 'base64 --decode %s > %s' % (
                    full_file_roots_state+file_name+'.p', full_file_roots_state + file_name+'.ps1'))

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

    include_salt = []
    all_salt_ins = {}
    count_success = count_fail = 0
    exec_transfer_file_result_filename = str(current_user) + "-" + ''.join(
        random.choices('0123456789', k=9)) + time.strftime(
        "%Y%m%d%H%M%S", time.localtime()) + '.txt'
    task_list.objects.filter(id=kwargs.get("new_task_id")).update(status=3, update_time=datetime.datetime.now())

    # get all salt for current user who owned
    current_user_salt = []
    current_user_salt_object = []
    current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=current_user)).values("rg")
    for each_user_rg in current_user_rgs:
        rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
        for each_rg_salt in rg_salt:
            current_user_salt.append(each_rg_salt["salt"])
    for each_user_salt in set(current_user_salt):
        current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))

    # get the relevant file attr
    transfer_file_object = transfer_file.objects.get(id=transfer_file_id)
    file_name = transfer_file_object.name
    file_dest_dir = json.loads(transfer_file_object.dest_dir)

    try:
        if host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name").first()[
            "salt_name"] is None:
            all_minions = host_group_minion.objects.filter(host_group_name=host_group_id).values("minion_name")
        else:
            for each_salt in host_group_minion.objects.filter(host_group_name=host_group_id).values("salt_name"):
                include_salt.append(each_salt["salt_name"])
            all_minions = hosts.objects.filter(salt__in=include_salt, status=0).values("name")

        for each_minion in all_minions:
            if each_minion.get("name", None) is None:
                each_minion = each_minion["minion_name"]
            else:
                each_minion = each_minion["name"]

            # Check whether the current user has permission to operate this node and whether the node is in the up state
            if (not hosts.objects.filter(name=each_minion, salt__in=current_user_salt_object)
                    or hosts.objects.filter(name=each_minion).values("status").first()["status"] != 0):
                count_fail += 1
                cleaned_content = "no permission or this minion status is not up"
                with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+', encoding="utf-8") as etfrf:
                    etfrf.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')
                continue

            # execute tasks asynchronously
            salt_server = salt_master.objects.get(
                id=hosts.objects.filter(name=each_minion).values("salt_id").first()["salt_id"])
            if salt_server.id not in all_salt_ins:
                salt_ins = SaltAPI(salt_server.host, salt_server.user, salt_server.password)
                all_salt_ins[salt_server.id] = salt_ins

            # according to kernel info to transfer file to minions
            minion_grains = all_salt_ins[salt_server.id].execute_grains(each_minion)["msg"][each_minion]
            if minion_grains and isinstance(minion_grains, dict):
                minion_kernel = minion_grains["kernel"]
                if file_dest_dir.get(minion_kernel, None):
                    src_dir = "salt://%s/%s" %(settings.SFTP_STORAGE_ROOT, file_name)
                    each_result = (all_salt_ins[salt_server.id].transfer_file(each_minion, src_dir, file_dest_dir[minion_kernel]) )
                    if each_result["status"] == 0 and each_result["msg"]:
                        count_success += 1
                        cleaned_content = "copy file successfully"
                    else:
                        count_fail += 1
                        cleaned_content = "failed to copy file"
                    with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+',
                              encoding="utf-8") as etfrf:
                        etfrf.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')
                else:
                    count_fail += 1
                    cleaned_content = "The minion kernel does not match the transfer directory"
                    with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+',
                              encoding="utf-8") as etfrf:
                        etfrf.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')
            else:
                count_fail += 1
                cleaned_content = "no valid information was obtained"
                with open(settings.DOWNLOAD_ROOT + exec_transfer_file_result_filename, 'a+', encoding="utf-8") as etfrf:
                    etfrf.write(f"{each_minion}:\n{cleaned_content}\n" + '\n')

    except Exception as e:
        logger.error(traceback.format_exc())

    return {"count_success": count_success, "count_fail": count_fail,
            "exec_remote_shell_result_filename": exec_transfer_file_result_filename}