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

import datetime
import random, re
from datetime import timedelta

import yaml

from .common.audit_action import audit_action
from .common.permission_ctrl import superuser_required, st_access_required

import time, os, requests, base64

from django.http import HttpResponse, Http404, FileResponse, HttpResponseRedirect, JsonResponse
import json, logging, traceback
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login as dj_login
from django.db import transaction
from django.conf import settings
from zoneinfo import ZoneInfo
from croniter import croniter
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count, Sum, Q

from django.shortcuts import render, redirect
from .models import *
from .common.salt_api import SaltAPI
from .common.notify_lark import send_lark_msg
from .common.parse_shell import parse_content
from django_q.tasks import async_task
from .tasks.hosts_list import register_hosts
from django_q.models import Task, Schedule
from storages.backends.sftpstorage import SFTPStorage
import paramiko
from ldap3 import Server, Connection, ALL

# Create your views here.
logger = logging.getLogger("default")

@login_required()
@audit_action
@csrf_exempt
def index(request):
    """dashboard页面"""
    hosts_num = hosts.objects.count()
    salt_num = salt_master.objects.count()
    users_num = User.objects.count()
    tasks_num = task_list.objects.count()

    # 根据时间获取工单分布趋势
    task_num_end_date = datetime.datetime.now()
    task_num_start_date = task_num_end_date - timedelta(days=9)
    task_tendency_data = (
        task_list.objects.filter(create_time__date__range=[task_num_start_date.date(), task_num_end_date.date()])
        .annotate(date=TruncDate('create_time'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    tasks_tendency = []
    for each_data in range(10):
        day = (task_num_start_date + timedelta(days=each_data)).date()
        formatted_day = day.strftime('%m-%d')
        count = next((item['count'] for item in task_tendency_data if item['date'] == day), 0)
        tasks_tendency.append({"date": formatted_day, "count": count})

    # 根据主机状态获取相关数量
    hosts_status_collect = {}
    for each_status in  [0, 1, 2, 3, 4, 5]:
        hosts_status_collect[each_status] = hosts.objects.filter(status=each_status).count()

    # 获取最近七天最活跃的用户
    task_user_end_date = datetime.datetime.now()
    task_user_start_date = task_user_end_date - timedelta(days=7)
    task_user_data = (
        task_list.objects.filter(create_time__date__range=[task_user_start_date.date(), task_user_end_date.date()])
        .values('user_id__username')
        .annotate(count=Count('id'))
    )
    task_user_tendency = [{'user': item['user_id__username'], 'count': item['count']} for item in task_user_data]
    while len(task_user_tendency) < 5:
        task_user_tendency.append({'user': "", 'count': ""})
    if len(task_user_tendency) > 5:
        task_user_tendency = task_user_tendency[:5]

    # 最近10天每天执行的主机数量
    task_execute_end_date = datetime.datetime.now()
    task_execute_start_date = task_execute_end_date - timedelta(days=9)

    # 查询最近10天的数据，按日期分组并计算 host_num 的总和
    task_execute_data = (
        task_list.objects.filter(create_time__date__range=[task_execute_start_date.date(), task_execute_end_date.date()])
        .annotate(date=TruncDate('create_time'))
        .values('date')
        .annotate(total_host_num=Sum('host_group_name__host_num'))
    )
    task_execute_result_dict = {item['date']: item['total_host_num'] for item in task_execute_data}

    for i in range(10):
        day = (task_execute_start_date + timedelta(days=i)).date()
        if day not in task_execute_result_dict:
            task_execute_result_dict[day] = 0

    task_execute_result_list = [
        {"date": day.strftime('%m-%d'), "count": task_execute_result_dict[day]}
        for day in sorted(task_execute_result_dict.keys())
    ]

    context = {
        "hosts_num": hosts_num,
        "salt_num": salt_num,
        "users_num": users_num,
        "tasks_num": tasks_num,
        "tasks_tendency": tasks_tendency,
        "hosts_status_collect": hosts_status_collect,
        "task_user_tendency": task_user_tendency,
        "task_execute_result_list": task_execute_result_list,

    }
    return render(request, "index.html", context=context)

@login_required()
@audit_action
@csrf_exempt
def show_message(request):
    task_messages = []
    if request.user.is_superuser:
        task_message = task_list.objects.filter(status=0).values("create_time", "name")[:3]
    else:
        task_message = task_list.objects.filter(status=0, user=request.user).values("create_time", "name")[:3]
    for each_task_message in task_message:
        task_messages.append({each_task_message["create_time"].strftime('%y-%m-%d %H:%M:%S'):each_task_message["name"]})
    count_task_message = task_message.count()
    authenticate_tag = authenticate_type.objects.get(name="authentication").type

    return HttpResponse(json.dumps({"count_task_message": count_task_message, "task_messages": task_messages, "authenticate_tag": authenticate_tag}), content_type="application/json")

@audit_action
@csrf_exempt
def login(request):
    if request.user.is_authenticated:
        return redirect("/index")
    else:
        if not authenticate_type.objects.filter(name="authentication"):
            authenticate_type.objects.create(type=0, name="authentication")
        authenticate_ins = authenticate_type.objects.get(name="authentication")

        # use internal to authenticate
        if authenticate_ins.type == 0:
            return render(request, "login.html")
        # use ldap to authenticate
        elif authenticate_ins.type == 1:
            return render(request, "login.html")
        # use oauth to authenticate
        elif authenticate_ins.type == 2:
            client_id = authenticate_ins.client_id
            redirect_url = authenticate_ins.redirect_url
            authorization_url = authenticate_ins.authorization_url
            full_url = "%s?client_id=%s&redirect_uri=%s" % (authorization_url, client_id, redirect_url)
            response_url = requests.get(full_url, timeout=10).url
            return HttpResponseRedirect(response_url)

@audit_action
@csrf_exempt
def authenticate_user(request):
    input_email = request.POST.get("input_email")
    input_password = request.POST.get("input_password")

    authenticate_result = {"status": 0, "msg": "ok"}
    if input_email and input_password:
        authenticate_ins = authenticate_type.objects.get(name="authentication")

        # use internal to authenticate
        if authenticate_ins.type == 0:
            user = authenticate(request, username=input_email, password=input_password)
            if user is not None and user.is_active:
                dj_login(request, user)
            else:
                authenticate_result["status"] = 1
                authenticate_result["msg"] = "用户名或密码错误，请重新输入"

        # use ldap to authenticate
        elif authenticate_ins.type == 1:
            try:
                ldap_server = Server(authenticate_ins.authorization_url, get_info=ALL, connect_timeout=10)
                user_dn = "uid=%s,%s" %(input_email, authenticate_ins.resource_url)
                ldap_conn = Connection(ldap_server, user=user_dn, password=input_password, receive_timeout=10)

                if ldap_conn.bind():
                    # make current user who are from ldap to login automatically
                    if not User.objects.filter(username=input_email):
                        User.objects.create_user(username=input_email, password="", is_superuser=0, is_active=1, is_staff=1)
                    user = authenticate(request, username=input_email, password="")
                    if user is not None and user.is_active:
                        dj_login(request, user)
                else:
                    authenticate_result["status"] = 1
                    authenticate_result["msg"] = "用户名或密码错误, 请重新输入"
            except Exception as e:
                logger.error(traceback.format_exc())
                authenticate_result["status"] = 1
                authenticate_result["msg"] = "连接Ldap服务器超时, 请检查"

    else:
        authenticate_result["status"] = 1
        authenticate_result["msg"] = "请输入完整的用户名和密码"

    return HttpResponse(json.dumps(authenticate_result), content_type="application/json")

@audit_action
@csrf_exempt
def logout_user(request):
    logout(request)
    authenticate_tag = 0
    if authenticate_tag == 0:
        return HttpResponse(json.dumps({"status": 0, "msg": "ok"}), content_type="application/json")
    else:
        # oauth authentication
        pass

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def list_masters(request):
    """
    展示所有salt master简略信息
    :param request:
    :return:
    """
    all_masters = salt_master.objects.filter(type=0)
    return render(request, "salt_masters.html", {"all_masters": all_masters})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def create_salt(request):
    salt_name = request.POST.get("input1")
    salt_desp = request.POST.get("input2")
    salt_host = request.POST.get("input3")
    salt_user = request.POST.get("input4")
    salt_password = request.POST.get("input5")
    minion_name = request.POST.get("input7")
    file_roots = request.POST.get("input8")
    salt_id = request.POST.get("input6")
    sftp_port = request.POST.get("input9")
    sftp_user = request.POST.get("input10")
    sftp_password = request.POST.get("input11")
    master_type = int(request.POST.get("master_type"))

    create_result = {"status":0, "msg":"ok"}
    file_roots_pattern = r'^[a-zA-Z0-9/_-]+$'

    try:

        if (master_type==0 and salt_name and salt_desp and salt_host and salt_user and salt_password and minion_name and file_roots
                and sftp_port and sftp_user and bool(re.match(file_roots_pattern, file_roots))):
            if salt_id:
                salt_master.objects.filter(id=salt_id).update(name=salt_name, description=salt_desp,
                                                              host=salt_host, user=salt_user, password=salt_password,
                                                              minion_name=minion_name, file_roots=file_roots,
                                                              sftp_port=sftp_port, sftp_user=sftp_user, sftp_password=sftp_password)
            else:
                salt_master.objects.create(name=salt_name, description=salt_desp, host=salt_host, user=salt_user,
                                           password=salt_password, minion_name=minion_name, file_roots=file_roots,
                                           sftp_port=sftp_port, sftp_user=sftp_user, sftp_password=sftp_password, type=master_type)

        elif (master_type==1 and salt_name and salt_desp and salt_user and file_roots
                and salt_password and sftp_port and bool(re.match(file_roots_pattern, file_roots))):
            if salt_id:
                salt_master.objects.filter(id=salt_id).update(name=salt_name, description=salt_desp,
                                                              user=salt_user, password=salt_password,
                                                              file_roots=file_roots, sftp_port=sftp_port)
            else:
                salt_master.objects.create(name=salt_name, description=salt_desp, host="", user=salt_user,
                                           password=salt_password, minion_name="", file_roots=file_roots,
                                           sftp_port=sftp_port, sftp_user="", sftp_password="", type=master_type)

        elif file_roots and not bool(re.match(file_roots_pattern, file_roots)):
            create_result["status"] = 1
            create_result["msg"] = "file_roots路径参数非法，请修正"

        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"

    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def del_salt(request):
    salt_id = request.POST.get("salt_id")

    del_result = {"status":0, "msg":"ok"}
    try:
        salt_master.objects.get(id=salt_id).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def check_salt_master(request):
    salt_host = request.POST.get("input3")
    salt_user = request.POST.get("input4")
    salt_password = request.POST.get("input5")

    check_result = {"status": 0, "msg": "Salt连接正常"}
    if salt_host and salt_user and salt_password:
        salt_instance = SaltAPI(url=salt_host, user=salt_user, passwd=salt_password)
        token_id = salt_instance.get_token()
        if not token_id:
            check_result["status"]=1
            check_result["msg"]="Salt Master访问不通，请检查配置"
    else:
        check_result["status"] = 1
        check_result["msg"] = "不完整的输入参数，请补全"

    return HttpResponse(json.dumps(check_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def check_sftp(request):
    sftp_host = request.POST.get("input3")
    sftp_port = request.POST.get("input9")
    sftp_user = request.POST.get("input10")
    sftp_password = request.POST.get("input11")
    file_roots = request.POST.get("input8")

    check_result = {"status": 0, "msg": "SFTP连接正常"}
    if not (sftp_host or sftp_port or sftp_user or sftp_password or file_roots):
        check_result["status"] = 1
        check_result["msg"] = "不完整的输入参数，请补全"
        return HttpResponse(json.dumps(check_result), content_type="application/json")
    if not ("//" in sftp_host and ":" in sftp_host):
        check_result["status"] = 1
        check_result["msg"] = "无效的Master API地址, 请检查协议和端口号"
        return HttpResponse(json.dumps(check_result), content_type="application/json")

    file_roots_pattern = r'^[a-zA-Z0-9/_-]+$'
    if not bool(re.match(file_roots_pattern, file_roots)):
        check_result["status"] = 1
        check_result["msg"] = "file_roots路径参数非法，请修正"
        return HttpResponse(json.dumps(check_result), content_type="application/json")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(sftp_host.split("//")[1].split(":")[0], port=sftp_port, username=sftp_user, password=sftp_password, timeout=10)
        check_cmd = "touch %s/test_permission_file" %(file_roots+'/'+settings.SFTP_STORAGE_ROOT)
        stdin, stdout, stderr = client.exec_command(check_cmd)
        stderr_output = stderr.read().decode()

        if stderr_output:
            check_result["status"] = 1
            check_result["msg"] = str(stderr_output.strip())
            return HttpResponse(json.dumps(check_result), content_type="application/json")

        client.exec_command("rm -f %s/test_permission_file" %(file_roots+'/'+settings.SFTP_STORAGE_ROOT))

    except Exception as e:
        logger.error(traceback.format_exc())
        check_result["status"] = 1
        check_result["msg"] = str(e)
    finally:
        client.close()

    return HttpResponse(json.dumps(check_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def list_shell_template(request):
    """
    展示所有salt master简略信息
    :param request:
    :return:
    """
    if request.user.is_superuser:
        all_shell = shell_template.objects.filter(history=0).all()
    else:
        all_shell = shell_template.objects.filter(user=request.user, history=0)

    state_home = settings.STATE_HOME

    return render(request, "shell_template.html", {"all_shell": all_shell, "state_home": state_home})

@login_required()
@audit_action
@csrf_exempt
def create_shell_template(request):
    """
    创建shell template，同时将shell template缩写为st.后面缩写均相同
    :param request:
    :return:
    """
    st_name = request.POST.get("st_name")
    st_des = request.POST.get("st_des")
    main_dir = request.POST.get("main_dir")
    editor_shell_content = request.POST.get("editor_shell_content")
    editor_sls_content = request.POST.get("editor_sls_content")
    editor_ps1_content = request.POST.get("editor_ps1_content")
    main_content = request.POST.get("main_content")
    extra_vars = request.POST.get("extra_vars")
    st_id = request.POST.get("input6")
    file_name = request.POST.get("file_name")
    check_type = int(request.POST.get("check_type"))

    # check playbook pattern
    check_result = {"status": 0, "msg": "ok"}
    if main_content:
        try:
            yaml.safe_load(main_content)
        except Exception as e:
            logger.error(traceback.format_exc())
            check_result["status"] = 1
            check_result["msg"] = "执行内容不符合yaml格式要求，请检查"
            return HttpResponse(json.dumps(check_result), content_type="application/json")

    create_result = {"status":0, "msg":"ok"}
    try:
        if st_name and st_des and (editor_shell_content or (editor_sls_content and file_name) or (main_dir and main_content)):
            if st_id:
                current_st = shell_template.objects.get(id=st_id)
                current_st.id = None
                current_st.name = st_name+"-"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                current_st.history = 1
                current_st.save()

                if check_type == 0:
                    shell_template.objects.filter(id=st_id).update(name=st_name, description=st_des, main_dir="",
                                                                   main_content=editor_sls_content,
                                                                   func_content=editor_ps1_content, extra_vars="",
                                                                   type=int(check_type), file_name=file_name,
                                                                   update_time=datetime.datetime.now())
                elif check_type == 1:
                    shell_template.objects.filter(id=st_id).update(name=st_name, description=st_des, main_dir="",
                                                                   main_content=editor_shell_content,
                                                                   func_content="", extra_vars="",
                                                                   type=int(check_type), file_name=file_name,
                                                                   update_time=datetime.datetime.now())
                else:
                    shell_template.objects.filter(id=st_id).update(name=st_name, description=st_des, main_dir=main_dir,
                                                                   main_content=main_content,
                                                                   func_content="", extra_vars=extra_vars,
                                                                   type=int(check_type), file_name=file_name,
                                                                   update_time=datetime.datetime.now())
            else:
                if check_type == 0:
                    shell_template.objects.create(name=st_name, description=st_des, main_dir="",
                                                  main_content=editor_sls_content,
                                                  func_content=editor_ps1_content, extra_vars="",
                                                  type=int(check_type), file_name=file_name, user=request.user)
                elif check_type == 1:
                    shell_template.objects.create(name=st_name, description=st_des, main_dir="",
                                                  main_content=editor_shell_content,
                                                  func_content="", extra_vars="",
                                                  type=int(check_type), file_name=file_name, user=request.user)
                else:
                    shell_template.objects.create(name=st_name, description=st_des, main_dir=main_dir,
                                                  main_content=main_content,
                                                  func_content="", extra_vars=extra_vars,
                                                  type=int(check_type), file_name=file_name, user=request.user)
        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def del_shell_template(request):
    st_id = request.POST.get("st_id")

    del_result = {"status":0, "msg":"ok"}
    try:
        shell_template.objects.get(id=st_id).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")

@login_required()
@audit_action
@st_access_required
@csrf_exempt
def list_sub_st(request, id):

    sub_st = sub_template.objects.filter(name=shell_template.objects.get(id=id), history=0)
    main_name = shell_template.objects.get(id=id).name
    return render(request, "sub_template.html", {"sub_st": sub_st, "main_name": main_name})


@login_required()
@audit_action
@csrf_exempt
def create_sub_st(request):
    st_id = request.POST.get("st_id")
    func_dir = request.POST.get("func_dir")
    func_content = request.POST.get("func_content")
    edit_st_id = request.POST.get("input6")
    create_result = {"status": 0, "msg": "ok"}
    try:
        if st_id and func_dir and func_content:
            if edit_st_id:
                current_st = sub_template.objects.get(id=edit_st_id)
                current_st.id = None
                current_st.history = 1
                current_st.save()

                sub_template.objects.filter(id=edit_st_id).update(name=shell_template.objects.get(id=st_id), func_dir=func_dir,
                                                             func_content=func_content, update_time=datetime.datetime.now())
            else:
                sub_template.objects.create(name=shell_template.objects.get(id=st_id), func_dir=func_dir, func_content=func_content)
        else:
            create_result["status"] = 1
            create_result["msg"] = "不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"] = 1
        create_result["msg"] = str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def del_sub_st(request):
    st_id = request.POST.get("st_id")

    del_result = {"status":0, "msg":"ok"}
    try:
        sub_template.objects.get(id=st_id).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")


@login_required()
@superuser_required
@audit_action
@csrf_exempt
def list_resource_group(request):
    """
    展示所有resource group信息.同时将resource group缩写为rg, 后面缩写均相同
    :param request:
    :return:
    """
    try:
        rg_saltname = {}
        rg_acl = {}
        all_masters_dic = {"amd":{}}

        all_masters = salt_master.objects.all()
        # 全量的salt master数据，格式为json.为双向选择框中渲染全部数据而准备
        for each_master in all_masters:
            all_masters_dic["amd"][each_master.id] = each_master.name
        all_rg = resource_group.objects.all()
        all_rg_salt = rg_relationship.objects.all()
        all_rg_salt_list = list(all_rg_salt.values("rg", "salt", "acl"))
        # 资源组与acl, salt名称的对应关系
        for each_rg_salt_list in all_rg_salt_list:
            if each_rg_salt_list["rg"] not in rg_acl:
                if each_rg_salt_list["acl"] is None:
                    each_rg_salt_list["acl"] = 0
                rg_acl[each_rg_salt_list["rg"]] = each_rg_salt_list["acl"]

            if each_rg_salt_list["rg"] not in rg_saltname:
                rg_saltname[each_rg_salt_list["rg"]] = {}
            rg_saltname[each_rg_salt_list["rg"]][each_rg_salt_list["salt"]]=salt_master.objects.get(id=each_rg_salt_list["salt"]).name

    except Exception as e:
        logger.error(traceback.format_exc())

    return render(request, "resource_group.html", {"rg_acl": rg_acl, "all_masters_dic": all_masters_dic, "all_masters": all_masters, "all_rg": all_rg, "rg_saltname": rg_saltname})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def create_resource_group(request):
    rg_name = request.POST.get("input1")
    rg_desp = request.POST.get("input2")
    acl_check = request.POST.get("aclcheck")
    selected_salt = set(request.POST.getlist("selectedValues[]"))
    rg_id = request.POST.get("input6")

    create_result = {"status":0, "msg":"ok"}
    try:
        if rg_name and rg_desp and selected_salt:
            if acl_check == "false":
                acl_foreign = None
            else:
                acl_foreign = acl_manage.objects.get(name="acl")
            with transaction.atomic():
                if rg_id:
                    rg_relationship.objects.filter(rg=rg_id).delete()
                    resource_group.objects.filter(id=rg_id).update(name=rg_name, description=rg_desp)
                else:
                    resource_group.objects.create(name=rg_name, description=rg_desp)
                for each_salt in selected_salt:
                        rg_relationship.objects.create(rg=resource_group.objects.get(name=rg_name),
                                                       salt=salt_master.objects.get(id=each_salt), acl=acl_foreign)
        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def del_resource_group(request):
    rg_id = request.POST.get("rg_id")
    print(rg_id)

    del_result = {"status":0, "msg":"ok"}
    try:
        with transaction.atomic():
            rg_relationship.objects.filter(rg=resource_group.objects.get(id=rg_id)).delete()
            resource_group.objects.get(id=rg_id).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def list_ro_setup(request):
    """
    展示所有acl信息.同时将readonly acl缩写为ro acl, 后面缩写均相同
    :param request:
    :return:
    """
    if not acl_manage.objects.filter(name="acl"):
        acl_manage.objects.create(name="acl", description="acl management", content="")
    all_acl = acl_manage.objects.all()

    return render(request, "ro_setup.html", {"all_acl": all_acl})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def create_acl(request):
    acl_desp = request.POST.get("input2")
    acl_id = request.POST.get("input6")
    acl_content = request.POST.get("input3")

    create_result = {"status":0, "msg":"ok"}
    try:
        if acl_content and acl_desp:
            if acl_id:
                acl_manage.objects.filter(id=acl_id).update(description=acl_desp, content=acl_content)
            else:
                acl_manage.objects.create(name="acl", description=acl_desp, content=acl_content)

        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def list_users(request):
    """
    展示所有用户相关信息
    :param request:
    :return:
    """
    try:
        all_users_dic = {}
        all_users = User.objects.filter()
        for each_user in all_users:
            all_users_dic[each_user.id] = [1 if each_user.is_superuser else 0, 1 if each_user.is_active else 0]

        all_rg_dic = {}
        all_rg = resource_group.objects.all()
        for each_rg in all_rg:
            all_rg_dic[each_rg.id] = each_rg.name

        user_relationship_dic = {}
        all_user_relationship = user_relationship.objects.all()
        for each_user_relationship in list(all_user_relationship.values("user", "rg")):
            if each_user_relationship["user"] not in user_relationship_dic:
                user_relationship_dic[each_user_relationship["user"]] = {}
            user_relationship_dic[each_user_relationship["user"]][each_user_relationship["rg"]]=all_rg_dic[each_user_relationship["rg"]]

    except Exception as e:
        logger.error(traceback.format_exc())

    return render(request, "user_manage.html", {"user_relationship_dic": user_relationship_dic, "all_users_dic": all_users_dic, "all_users": all_users, "all_rg": all_rg, "all_rg_dic": all_rg_dic})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def create_user_relationship(request):
    username = request.POST.get("input1")
    password = request.POST.get("input2")
    confirm_pwd = request.POST.get("input3")
    email = request.POST.get("input5")
    user_id = request.POST.get("input6")
    superuser_check = json.loads(request.POST.get("superusercheck").lower())
    user_check = json.loads(request.POST.get("usercheck").lower())
    selected_rg = set(request.POST.getlist("selectedValues[]"))

    create_result = {"status":0, "msg":"ok"}
    try:
        if username and email and selected_rg:
            with transaction.atomic():
                if user_id:
                    # update
                    User.objects.filter(id=user_id).update(username=username, is_superuser=superuser_check, email=email, is_active=user_check)
                    user_relationship.objects.filter(user=User.objects.get(id=user_id)).delete()
                    for each_rg in selected_rg:
                        user_relationship.objects.create(user=User.objects.get(id=user_id), rg=resource_group.objects.get(id=each_rg))
                else:
                    # create new one
                    if  password and confirm_pwd:
                        if password == confirm_pwd and "@" in email:
                            User.objects.create_user(username=username, password=password, is_superuser=superuser_check, email=email, is_active=user_check)
                            for each_rg in selected_rg:
                                user_relationship.objects.create(user=User.objects.get(username=username), rg=resource_group.objects.get(id=each_rg))
                        else:
                            raise ValueError("两次输入密码不匹配或邮箱格式不正确,请检查")
                    else:
                        raise ValueError("密码为空，请输入")

        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def del_user(request):
    user_id = request.POST.get("user_id")
    del_result = {"status":0, "msg":"ok"}
    try:
        with transaction.atomic():
            user_relationship.objects.filter(user=User.objects.get(id=user_id)).delete()
            User.objects.get(id=user_id).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def get_hosts(request):
    """
    分页展示所有受管服务器相关信息
    :param request:
    :return:
    """
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    reverse_host_status_choices = {rhsc_v:rhsc_k for rhsc_k, rhsc_v in dict(hosts.host_status_choices).items()}

    query = hosts.objects.select_related("salt")
    if search_value:
        query = query.filter(Q(name__icontains=search_value) | Q(status__icontains=reverse_host_status_choices.get(search_value, 100))
                             | Q(salt__name__icontains=search_value) | Q(update_time__icontains=search_value))

    total_count = query.count()
    data = list(query[start:start + length].values("id", "name", "status", "salt__name", "update_time"))
    for each_data in data:
        # 获取每个对象的显示值
        each_data['status_display'] = dict(hosts.host_status_choices).get(each_data['status'])

    return JsonResponse({
        "draw": int(request.GET.get('draw', 1)),
        "recordsTotal": hosts.objects.count(),
        "recordsFiltered": total_count,
        "data": data
    })

@login_required()
@audit_action
@csrf_exempt
def list_hosts(request):
    """
    展示所有受管服务器相关信息
    :param request:
    :return:
    """
    all_hosts = hosts.objects.select_related("salt")
    refrsh_interval = settings.FRESH_INTERVAL

    return render(request, "hosts.html", {"refrsh_interval": refrsh_interval})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def setup_host(request):
    """
    处理host的三种状态, accept, reject, delete
    :param request:
    :return:
    """
    setup_type = request.POST.get("setup_type")
    setup_salt = request.POST.get("setup_salt")
    setup_result = {"status":0, "msg":"ok"}

    try:
        host_name = setup_type[2:]
        salt_host = salt_master.objects.get(name=setup_salt)
        salt_ins = SaltAPI(url=salt_host.host, user=salt_host.user, passwd=salt_host.password)

        with transaction.atomic():
            if setup_type.startswith("a-"):
                accept_key_result = salt_ins.accept_key(host_name)
                if accept_key_result["status"] == 0:
                    match_host = hosts.objects.filter(name=host_name, salt=salt_host).first()
                    match_host.status = 0
                    match_host.save()
            elif setup_type.startswith("r-"):
                reject_key_result = salt_ins.reject_key(host_name)
                if reject_key_result["status"] == 0:
                    match_host = hosts.objects.filter(name=host_name, salt=salt_host).first()
                    match_host.status = 5
                    match_host.save()
            elif setup_type.startswith("d-"):
                del_key_result = salt_ins.delete_key(host_name)
                if del_key_result["status"] == 0:
                    hosts.objects.filter(name=host_name, salt=salt_host).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        setup_result["status"]=1
        setup_result["msg"]=str(e)

    return HttpResponse(json.dumps(setup_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def refresh_minion(request):
    """
    刷新minion节点在数据库的状态信息
    :param request:
    :return:
    """
    refresh_result = {"status": 0, "msg": "ok"}

    # 第一次初始化minion定时刷新任务，之后不再需要
    if not Schedule.objects.filter(func="salt.tasks.hosts_list.register_hosts"):
        Schedule.objects.create(func="salt.tasks.hosts_list.register_hosts", schedule_type=Schedule.MINUTES,
                                minutes=settings.FRESH_INTERVAL, hook='salt.tasks.q_task.running_task')
    if Schedule.objects.get(func="salt.tasks.hosts_list.register_hosts").minutes != settings.FRESH_INTERVAL:
        Schedule.objects.filter(func="salt.tasks.hosts_list.register_hosts").update(minutes=settings.FRESH_INTERVAL)

    # 标记刷新任务执行状态, success=0是没有正在执行的刷新任务，success=1是有
    if not Task.objects.filter(id="refresh_label"):
        Task.objects.create(name="refresh_label", func="salt.tasks.hosts_list.register_hosts",
                            started=datetime.datetime.now(), stopped=datetime.datetime.now(),
                            success=0, id="refresh_label", attempt_count=0)

    # 如果在10分钟内有开始的定时刷新任务，则等待自动刷新，拒绝手工刷新操作
    current_time = datetime.datetime.now().astimezone(ZoneInfo(settings.FRESH_TIMEZONE))
    next_run_time = Schedule.objects.get(func="salt.tasks.hosts_list.register_hosts").next_run
    if next_run_time - timedelta(seconds=600) < current_time:
        Task.objects.filter(id="refresh_label").update(success=1, started=datetime.datetime.now())

    if Task.objects.filter(id="refresh_label", success=1):
        refresh_result["status"] = 1
        refresh_result["msg"] = "目前已有刷新任务正在执行，请稍等"
    else:
        async_task(register_hosts, hook='salt.tasks.q_task.running_task')

    return HttpResponse(json.dumps(refresh_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def list_host_group(request):
    """
    展示所有主机组相关信息
    :param request:
    :return:
    """
    current_user_salt = []
    current_user_salt_object = []

    try:
        if request.user.is_superuser:
            all_host_group = host_group.objects.all()
        else:
            all_host_group = host_group.objects.filter(user=User.objects.get(username=request.user)).all()
        current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=request.user)).values("rg")
        for each_user_rg in current_user_rgs:
            rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
            for each_rg_salt in rg_salt:
                current_user_salt.append(each_rg_salt["salt"])
        for each_user_salt in set(current_user_salt):
            current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))
        hosts_limited = hosts.objects.filter(salt__in=current_user_salt_object)
        user_salt_info = salt_master.objects.filter(id__in=set(current_user_salt), type=0)
        user_an_info = salt_master.objects.filter(id__in=set(current_user_salt), type=1)

    except Exception as e:
        logger.error(traceback.format_exc())

    return render(request, "host_group.html", {"user_salt_info": user_salt_info, "user_an_info": user_an_info, "all_host_group": all_host_group, "hosts_limited": hosts_limited})

@login_required()
@audit_action
@csrf_exempt
def create_host_group(request):
    name = request.POST.get("input1")
    description = request.POST.get("input5")
    host_group_id = request.POST.get("input6")
    selected_salt = set(request.POST.getlist("selectedValues[]"))
    selected_host = set(request.POST.getlist("selectedHostValues[]"))
    selected_host_with_upload = request.POST.getlist("upload_label")
    upload_hg_executed = int(request.POST.get("upload_hg_executed"))
    an_master = request.POST.get("an_master")

    create_result = {"status":0, "msg":"ok"}
    include_num = 0
    try:
        if host_group_id and name and description:
            # edit one host_group
            edited_hg = host_group.objects.get(id=host_group_id[3:])
            if selected_salt:
                with transaction.atomic():
                    for each_salt in selected_salt:
                        include_num = include_num + hosts.objects.filter(salt=salt_master.objects.get(id=each_salt), status=0).count()
                    edited_hg.name = name
                    edited_hg.description = description
                    edited_hg.host_num = include_num
                    edited_hg.save()

                    host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id[3:])).delete()
                    for each_master in selected_salt:
                        host_group_minion.objects.create(host_group_name=host_group.objects.get(id=host_group_id[3:]), salt_name=salt_master.objects.get(id=each_master))
            elif selected_host:
                with transaction.atomic():
                    edited_hg.name = name
                    edited_hg.description = description
                    edited_hg.host_num = len(selected_host)
                    edited_hg.save()

                    host_group_minion.objects.filter(host_group_name=host_group.objects.get(id=host_group_id[3:])).delete()
                    for each_host in selected_host:
                        host_group_minion.objects.create(host_group_name=host_group.objects.get(id=host_group_id[3:]),
                                                         minion_name=hosts.objects.get(id=each_host).name if each_host.isnumeric() else each_host)

        elif name and description and (selected_salt or selected_host or (selected_host_with_upload[0]!='0' and selected_host_with_upload[0]!="")):
            # create new one
            if selected_salt:
                with transaction.atomic():
                    for each_salt in selected_salt:
                        include_num = include_num + hosts.objects.filter(salt=salt_master.objects.get(id=each_salt), status=0).count()
                    host_group.objects.create(name=name, description=description, host_num=include_num, user=User.objects.get(username=request.user))
                    for each_master in selected_salt:
                        host_group_minion.objects.create(host_group_name=host_group.objects.get(name=name), salt_name=salt_master.objects.get(id=each_master))
            elif selected_host:
                with transaction.atomic():
                    host_group.objects.create(name=name, description=description, host_num=len(selected_host), user=User.objects.get(username=request.user))
                    for each_host in selected_host:
                        host_group_minion.objects.create(host_group_name=host_group.objects.get(name=name),
                                                         minion_name=hosts.objects.get(id=each_host).name)
            else:
                if not os.path.exists(settings.DOWNLOAD_ROOT+"up-"+selected_host_with_upload[0]):
                    raise Http404("文件不存在, 请联系管理员")
                with open(settings.DOWNLOAD_ROOT+"up-"+selected_host_with_upload[0], 'r') as file:
                    content = file.readlines()
                with transaction.atomic():
                    if upload_hg_executed == 0:
                        host_group.objects.create(name=name, description=description, host_num=len(content), user=User.objects.get(username=request.user))
                        for each_host in content:
                            host_group_minion.objects.create(host_group_name=host_group.objects.get(name=name),
                                                             minion_name=hosts.objects.get(name=each_host.strip(), status=0).name)
                    else:
                        host_group.objects.create(name=name, description=description, host_num=len(content), type=1, user=User.objects.get(username=request.user))
                        for each_host in content:
                            host_group_minion.objects.create(host_group_name=host_group.objects.get(name=name),
                                                                 minion_name=each_host.strip(), salt_name=salt_master.objects.get(id=an_master))

        else:
            create_result["status"]=1
            create_result["msg"]="不完整的输入参数，请补全"
    except Exception as e:
        logger.error(traceback.format_exc())
        create_result["status"]=1
        create_result["msg"]=str(e)

    return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def read_file(request):
    read_result = {"status": 0, "msg": "ok", "filename": ""}

    current_user_salt = []
    current_user_salt_object = []
    current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=request.user)).values("rg")
    for each_user_rg in current_user_rgs:
        rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
        for each_rg_salt in rg_salt:
            current_user_salt.append(each_rg_salt["salt"])
    for each_user_salt in set(current_user_salt):
        current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))

    try:
        if request.method == 'POST':
            file = request.FILES.get('file')
            upload_hg_executed = int(request.POST.get("upload_hg_executed"))
            up_hosts = 0
            non_up_hosts = 0
            host_group_filename = str(request.user) + ''.join(random.choices('0123456789', k=7)) + time.strftime(
                "%Y%m%d%H%M%S", time.localtime()) + '.txt'

            if file:
                file_content = file.read().decode('utf-8')
                for each_minion in file_content.splitlines():
                    if not each_minion:
                        break

                    if upload_hg_executed == 0:
                        filter_host = hosts.objects.filter(name__icontains=each_minion, status=0, salt__in=current_user_salt_object)
                    else:
                        filter_host = each_minion

                    if filter_host:
                        up_hosts = up_hosts+1
                        if upload_hg_executed == 0:
                            with open(settings.DOWNLOAD_ROOT+"up-"+host_group_filename, 'a+') as up_hgf:
                                up_hgf.write(filter_host.first().name+'\n')
                        else:
                            with open(settings.DOWNLOAD_ROOT+"up-"+host_group_filename, 'a+') as up_hgf:
                                up_hgf.write(filter_host+'\n')
                    else:
                        non_up_hosts = non_up_hosts+1
                        with open(settings.DOWNLOAD_ROOT+host_group_filename, 'a+') as hgf:
                            hgf.write(each_minion+'\n')
                read_result["msg"] = (
                    "筛选正常主机有 {0} 台，非正常主机有 {1} 台。请查看主机分组详情仔细检查核对主机信息 <br>"
                    "非正常主机具体信息请下载附件查看"
                ).format(up_hosts, non_up_hosts, host_group_filename)
                read_result["filename"] = host_group_filename

            else:
                read_result["status"]=1
                read_result["msg"]="不正确的文件格式或内容, 请检查"

    except Exception as e:
        logger.error(traceback.format_exc())
        read_result["status"]=1
        read_result["msg"]=str(e)

    return HttpResponse(json.dumps(read_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def download_hg(request):
    filename = request.POST.get("filename")

    if filename:
        file_path = os.path.join(settings.DOWNLOAD_ROOT, filename)

        if not os.path.exists(file_path):
            raise Http404("文件不存在, 请联系管理员")

        with open(file_path, 'r') as hg_file:
            hg_content = hg_file.read()
        # 返回文件内容作为 HTTP 响应，设置为 text/plain 格式
        response = HttpResponse(hg_content, content_type='text/plain')
        # 让浏览器在新 tab 中显示文件
        response['Content-Disposition'] = 'inline; filename=%s' %filename

        return response

@login_required()
@audit_action
@csrf_exempt
def del_host_group(request):
    host_group_name = request.POST.get("host_group_name")
    del_result = {"status":0, "msg":"ok"}

    try:
        with transaction.atomic():
            host_group_minion.objects.filter(host_group_name=host_group.objects.get(name=host_group_name)).delete()
            host_group.objects.get(name=host_group_name).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        del_result["status"]=1
        del_result["msg"]=str(e)

    return HttpResponse(json.dumps(del_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def show_selected_host_group(request):
    host_group_name = request.POST.get("host_group_name")
    selected_minions_salts_list = {"type": 0, "content": []}

    try:
        if host_group_minion.objects.filter(
            host_group_name=host_group.objects.get(name=host_group_name), minion_name=""):
            selected_host_group = host_group_minion.objects.filter(
                host_group_name=host_group.objects.get(name=host_group_name)).values("host_group_name__name",
                                                                                     "salt_name__name")

            # put all salts in list
            selected_minions_salts = host_group_minion.objects.filter(
                host_group_name=host_group.objects.get(name=host_group_name)).values("salt_name",
                                                                                     "salt_name__name")
            for each_selected_minions_salts in selected_minions_salts:
                selected_minions_salts_list["content"].append({"id":each_selected_minions_salts["salt_name"], "name":each_selected_minions_salts["salt_name__name"]})

        else:
            selected_host_group = host_group_minion.objects.filter(
                host_group_name=host_group.objects.get(name=host_group_name)).values("host_group_name__name",
                                                                                     "minion_name")

            # put all minions in list
            selected_minions_salts = host_group_minion.objects.filter(
                host_group_name=host_group.objects.get(name=host_group_name)).values("minion_name")
            selected_minions_salts_list["type"] = 1
            # confirm that these nodes are from salt or ansible
            if host_group.objects.get(name=host_group_name).type == 1:
                selected_minions_salts_list["type"] = 2

            for each_selected_minions_salts in selected_minions_salts:
                selected_minions_salts_list["content"].append({"id": each_selected_minions_salts["minion_name"],
                                                               "name": each_selected_minions_salts["minion_name"]})

        context = {
            "selected_host_group": json.dumps(list(selected_host_group)),
            "selected_minions_salts_list": selected_minions_salts_list,
        }

        return HttpResponse(json.dumps(context), content_type="application/json")

    except Exception as e:
        logger.error(traceback.format_exc())

@login_required()
@audit_action
@csrf_exempt
def search_available_host(request):
    search_content = request.POST.get("searchHostInput")
    search_result = {"status":0, "msg":"ok", "content":""}

    try:
        current_user_salt = []
        current_user_salt_object = []
        current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=request.user)).values("rg")
        for each_user_rg in current_user_rgs:
            rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values(
                "salt")
            for each_rg_salt in rg_salt:
                current_user_salt.append(each_rg_salt["salt"])
        for each_user_salt in set(current_user_salt):
            current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))
        search_hosts = hosts.objects.filter(salt__in=current_user_salt_object, name__icontains=search_content).values("id", "name")
        search_result["content"] = list(search_hosts)

    except Exception as e:
        logger.error(traceback.format_exc())
        search_result["status"]=1
        search_result["msg"]=str(e)

    return HttpResponse(json.dumps(search_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def create_shell_task(request):
    """
    对主机批量执行操作
    :param request:
    :return:
    """
    custom_url = request.scheme+"://"+request.get_host()+"/list_tasks/"
    create_result = {"status": 0, "msg": "ok"}
    # show all host group of user
    if request.method == 'GET':
        current_user_salt = []
        current_user_salt_object = []
        if request.user.is_superuser:
            all_host_group = host_group.objects.all()
        else:
            all_host_group = host_group.objects.filter(user=User.objects.get(username=request.user)).all()
        current_user_rgs = user_relationship.objects.filter(user=User.objects.get(username=request.user)).values("rg")
        for each_user_rg in current_user_rgs:
            rg_salt = rg_relationship.objects.filter(rg=resource_group.objects.get(id=each_user_rg["rg"])).values("salt")
            for each_rg_salt in rg_salt:
                current_user_salt.append(each_rg_salt["salt"])
        for each_user_salt in set(current_user_salt):
            current_user_salt_object.append(salt_master.objects.get(id=each_user_salt))
        hosts_limited = hosts.objects.filter(salt__in=current_user_salt_object)
        user_salt_info = salt_master.objects.filter(id__in=set(current_user_salt))

        if request.user.is_superuser:
            all_shell = shell_template.objects.filter(history=0).values("id", "name")
            all_transfer_file = transfer_file.objects.all().values("id", "name")
        else:
            all_shell = shell_template.objects.filter(user=request.user, history=0).values("id", "name")
            all_transfer_file = transfer_file.objects.filter(user=request.user).values("id", "name")

        return render(request, "remote_shell.html", {"user_salt_info": user_salt_info, "all_host_group": all_host_group,
                                                     "hosts_limited": hosts_limited, "all_shell": all_shell, "all_transfer_file": all_transfer_file})

    # create new task
    if request.method == 'POST':
        exec_content = request.POST.get("exec_content")
        immediate_checked = request.POST.get("radio1_checked")
        schedule_checked = request.POST.get("radio2_checked")
        hg_id = request.POST.get("hg_id")
        exec_shell_template = request.POST.get("exec_shell_template")
        exec_transfer_file = request.POST.get("exec_transfer_file")
        task_name = request.POST.get("task_name")
        repeat_num = request.POST.get("repeat_num")

        try:
            if ((exec_content or exec_shell_template or exec_transfer_file) and (immediate_checked!="0" or schedule_checked!="0")
                    and hg_id and task_name and repeat_num):
                # Encapsulate exec_content to dict, and 0 stands for int, 1 stands for str
                encap_exec_content = {"content": base64.b64encode(exec_content.encode()).decode() if exec_content is not None else exec_content, "type": 1}

                # check if the repeat_num is an integer
                # if not bool(re.match(r'^[-+]?\d+$', repeat_num)):
                #     create_result["status"] = 1
                #     create_result["msg"] = "执行频率选项必须是整数, 请重新输入"
                #     raise ValueError(create_result["msg"])

                # confirm execute type, include immediate and schedule
                if immediate_checked == "0":
                    if len(schedule_checked.split()) != 5:
                        create_result["status"] = 1
                        create_result["msg"] = "请输入合法的定时参数"
                        raise ValueError(create_result["msg"])
                    else:
                        exec_type = schedule_checked
                else:
                    exec_type = immediate_checked
                # get the template object
                if exec_shell_template is not None:
                    encap_exec_content["content"] = exec_shell_template
                    encap_exec_content["type"] = 0
                    exec_content = shell_template.objects.get(id=exec_shell_template).main_content

                # check the type(salt or ansible) of host group
                if host_group.objects.get(id=hg_id).type == 0:
                    run_command_func = "salt.tasks.exec_task.exec_remote_shell"
                    copy_file_func = "salt.tasks.exec_task.exec_transfer_file"
                else:
                    run_command_func = "ansible.tasks.exec_task.exec_remote_shell"
                    copy_file_func = "ansible.tasks.exec_task.exec_transfer_file"

                # parse exe_content to confirm that if it matched read-only policy
                parse_result = parse_content(exec_content)
                if parse_result["status"] == 0:
                    with transaction.atomic():
                        new_task = task_list.objects.create(name=task_name, execute_content=exec_content, execute_policy=exec_type,
                                                 host_group_name=host_group.objects.get(id=hg_id), user=User.objects.get(username=request.user),
                                                            status=1, repeat_num=int(repeat_num))

                        if exec_type == "1":
                            next_run_time = new_task.update_time + timedelta(seconds=10)
                            schedule_checked = "* * * * *"
                        else:
                            cron_format = croniter(schedule_checked, timezone.now())
                            next_run_time = datetime.datetime.fromtimestamp(cron_format.get_next())
                        new_schedule = Schedule.objects.create(func=run_command_func,
                                                args="(%d, '%s', '%s')" %(int(hg_id), json.dumps(encap_exec_content), str(request.user)),
                                                schedule_type=Schedule.CRON,
                                                cron=schedule_checked,
                                                repeats=int(repeat_num),
                                                next_run=next_run_time,
                                                hook="salt.tasks.q_task.remote_shell_task",
                                                kwargs=json.dumps({"new_task_id": new_task.id, "custom_url": custom_url})
                                                )
                        task_list.objects.filter(id=new_task.id).update(related_schedule=new_schedule.id, approver=request.user, approve_result = "自动通过")
                    send_lark_msg(task_name=task_name, current_user=str(request.user),
                                  message="已成功创建, 自动审批通过, 进入待执行状态, 请及时关注任务状态变化")
                elif (exec_content or exec_shell_template) and not exec_transfer_file:
                    with transaction.atomic():
                        new_task = task_list.objects.create(name=task_name, execute_content=exec_content, execute_policy=exec_type,
                                                 host_group_name=host_group.objects.get(id=hg_id), user=User.objects.get(username=request.user),
                                                            status=0, repeat_num=int(repeat_num))
                        new_schedule = Schedule.objects.create(func=run_command_func,
                                                args="(%d, '%s', '%s')" %(int(hg_id), json.dumps(encap_exec_content), str(request.user)),
                                                schedule_type=Schedule.CRON,
                                                cron="",
                                                repeats=0,
                                                hook="salt.tasks.q_task.remote_shell_task",
                                                kwargs=json.dumps({"new_task_id": new_task.id, "custom_url": custom_url})
                                                )
                        task_list.objects.filter(id=new_task.id).update(related_schedule=new_schedule.id)
                    send_lark_msg(task_name=task_name, current_user=str(request.user),
                                  message="已成功创建, 等待被审批, 请及时关注任务状态变化")
                elif not (exec_content and exec_shell_template) and exec_transfer_file:
                    with transaction.atomic():
                        new_task = task_list.objects.create(name=task_name, execute_content='transfer file: '+transfer_file.objects.get(id=exec_transfer_file).name,
                                                            execute_policy=exec_type,
                                                            host_group_name=host_group.objects.get(id=hg_id),
                                                            user=User.objects.get(username=request.user), status=0, repeat_num=int(repeat_num))
                        new_schedule = Schedule.objects.create(func=copy_file_func,
                                                               args="(%d, '%s', '%s')" % (
                                                               int(hg_id), int(exec_transfer_file),
                                                               str(request.user)),
                                                               schedule_type=Schedule.CRON,
                                                               cron="",
                                                               repeats=0,
                                                               hook="salt.tasks.q_task.remote_shell_task",
                                                               kwargs=json.dumps({"new_task_id": new_task.id, "custom_url": custom_url})
                                                               )
                        task_list.objects.filter(id=new_task.id).update(related_schedule=new_schedule.id)
                    send_lark_msg(task_name=task_name, current_user=str(request.user), message="已成功创建, 等待被审批, 请及时关注任务状态变化")

            else:
                create_result["status"] = 1
                create_result["msg"] = "请输入完整参数"

        except Exception as e:
            logger.error(traceback.format_exc())
            create_result["status"] = 1
            create_result["msg"] = str(e)

        return HttpResponse(json.dumps(create_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def list_tasks(request):
    """
    展示用户相关任务
    :param request:
    :return:
    """
    if request.user.is_superuser:
        all_tasks = task_list.objects.all()
    else:
        all_tasks = task_list.objects.filter(user=User.objects.get(username=request.user)).all()

    return render(request, "task_list.html", {"all_tasks": all_tasks})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def approve_task(request):
    """
    审批同意任务工单
    :param request:
    :return:
    """
    task_id = request.POST.get("task_id")

    approve_result = {"status": 0, "msg": "ok"}
    try:
        task_info = task_list.objects.get(id=int(task_id))
        task_info.status = 1
        task_info.approve_result = "同意"
        task_info.approver = request.user
        task_info.save()
        update_time = task_info.update_time
        execute_policy = task_info.execute_policy
        schedule_id = task_info.related_schedule
        repeat_num = task_info.repeat_num

        if execute_policy == "1":
            execute_time = update_time + timedelta(minutes=2)
            Schedule.objects.filter(id=schedule_id).update(next_run=execute_time, repeats=repeat_num, cron="* * * * *")
        else:
            cron_format = croniter(execute_policy, timezone.now())
            next_run_time = datetime.datetime.fromtimestamp(cron_format.get_next())
            Schedule.objects.filter(id=schedule_id).update(next_run=next_run_time, repeats=repeat_num, cron=execute_policy)

        send_lark_msg(task_name=task_info.name, current_user=str(task_info.user), message="已被审批通过, 进入待执行状态")
    except Exception as e:
        logger.error(traceback.format_exc())
        approve_result["status"] = 1
        approve_result["msg"] = str(e)

    return HttpResponse(json.dumps(approve_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def withdraw_task(request):
    """
    撤回任务工单
    :param request:
    :return:
    """
    task_id = request.POST.get("task_id")

    withdraw_result = {"status": 0, "msg": "ok"}
    try:
        task_info = task_list.objects.get(id=int(task_id))
        if task_info.status == 0:
            task_info.status = 5
            task_info.save()

            send_lark_msg(task_name=task_info.name, current_user=str(request.user),
                          message="已被撤回")
        else:
            withdraw_result["status"] = 1
            withdraw_result["msg"] = "当前工单状态不支持被撤回"

    except Exception as e:
        logger.error(traceback.format_exc())
        withdraw_result["status"] = 1
        withdraw_result["msg"] = str(e)

    return HttpResponse(json.dumps(withdraw_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def stop_task(request):
    """
    终止任务工单
    :param request:
    :return:
    """
    task_id = request.POST.get("task_id")

    stop_result = {"status": 0, "msg": "ok"}
    try:
        with transaction.atomic():
            task_info = task_list.objects.get(id=int(task_id))
            if task_info.status == 1 or task_info.status == 3:
                task_info.status = 6
                task_info.save()

                send_lark_msg(task_name=task_info.name, current_user=str(task_info.user),
                              message="已被终止")
            else:
                stop_result["status"] = 1
                stop_result["msg"] = "当前工单状态不支持被终止"

            Schedule.objects.filter(id=task_info.related_schedule).update(repeats=0)

    except Exception as e:
        logger.error(traceback.format_exc())
        stop_result["status"] = 1
        stop_result["msg"] = str(e)

    return HttpResponse(json.dumps(stop_result), content_type="application/json")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def reject_task(request):
    """
    审批拒绝任务工单
    :param request:
    :return:
    """
    task_id = request.POST.get("task_id")
    reject_reason = request.POST.get("reject_reason")

    reject_result = {"status": 0, "msg": "ok"}
    if len(reject_reason) == 0:
        reject_result["status"] = 1
        reject_result["msg"] = "拒绝原因不可为空"
    else:
        try:
            task_info = task_list.objects.get(id=int(task_id[2:]))
            task_info.status = 4
            task_info.approve_result = reject_reason
            task_info.approver = request.user
            task_info.save()

            send_lark_msg(task_name=task_info.name, current_user=str(task_info.user),
                          message="已被拒绝，请及时联系管理员")
        except Exception as e:
            logger.error(traceback.format_exc())
            reject_result["status"] = 1
            reject_result["msg"] = str(e)

    return HttpResponse(json.dumps(reject_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def get_task_info(request):
    """
    获取任务工单信息
    :param request:
    :return:
    """
    task_id = request.POST.get("task_id")

    get_task_result = {"status": 0, "msg": "ok"}
    try:
        task_info = task_list.objects.get(id=task_id)
        get_task_result["msg"] = json.loads(task_info.execute_result.replace("'", '"') if task_info.execute_result else '{}')
        get_task_result["shell"] = task_info.execute_content
        get_task_result["approve_result"] = task_info.approve_result
        get_task_result["approve_status"] = task_info.status
        superuser_list = []
        for each_superuser in User.objects.filter(is_superuser=True):
            superuser_list.append(each_superuser.username)
        get_task_result["superuser_list"] = str(superuser_list)

    except Exception as e:
        logger.error(traceback.format_exc())
        get_task_result["status"] = 1
        get_task_result["msg"] = str(e)

    return HttpResponse(json.dumps(get_task_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def download_execute_result(request):
    filename = request.POST.get("filename")

    if filename:
        file_path = os.path.join(settings.DOWNLOAD_ROOT, filename)

        if not os.path.exists(file_path):
            raise Http404("文件不存在, 请联系管理员")

        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def get_audit_info(request):
    """
    分页显示所有审计信息
    :param request:
    :return:
    """
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    query = general_audit.objects.all()
    if search_value:
        query = query.filter(Q(user__username__icontains=search_value) | Q(action__icontains=search_value) | Q(extra_content__icontains=search_value) | Q(create_time__icontains=search_value))

    total_count = query.count()
    data = list(query[start:start + length].values("id", "user__username", "action", "extra_content", "create_time"))

    return JsonResponse({
        "draw": int(request.GET.get('draw', 1)),
        "recordsTotal": general_audit.objects.count(),
        "recordsFiltered": total_count,
        "data": data
    })

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def audit_info(request):

    return render(request, "audit_action.html")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def authenticate_mgmt(request):
    return render(request, "authentication_mgmt.html")

@audit_action
@csrf_exempt
def callback_oauth(request):
    client_code = request.GET.get("code")

    authenticate_ins = authenticate_type.objects.get(name="authentication")
    access_token_url = authenticate_ins.access_token_url
    client_id = authenticate_ins.client_id
    client_secret = authenticate_ins.client_secret
    redirect_url = authenticate_ins.redirect_url
    resource_url = authenticate_ins.resource_url
    grant_type = authenticate_ins.grant_type if authenticate_ins.grant_type else "authorization_code"

    if client_code and access_token_url and client_id and client_secret and redirect_url and resource_url:
        request_access_token_data = {"grant_type": grant_type, "client_id": client_id, "client_secret": client_secret, "code": client_code,
                        "redirect_uri": redirect_url}
        request_headers = {"Authorization": "Bearer token", "Content-Type": "application/json; charset=utf-8"}
        response_content = requests.post(access_token_url, json=request_access_token_data, headers=request_headers, timeout=10)
        json_response_content = json.loads(response_content.content)
        if json_response_content["code"] == 0:
            user_access_token = json_response_content["token_type"] + " "+ json_response_content["access_token"]
            request_resource_data = {"Authorization": user_access_token, "Content-Type": "application/json; charset=utf-8"}
            user_info = requests.get(url=resource_url, headers=request_resource_data)
            json_user_info = json.loads(user_info.content)
            username = json_user_info["data"]["email"].split("@")[0] if "@" in json_user_info["data"]["email"] else json_user_info["data"]["email"]
            email = json_user_info["data"]["email"]

            # make current user who are from oauth to login automatically
            if not User.objects.filter(username=username):
                User.objects.create_user(username=username, password="", is_superuser=0, email=email,
                                         is_active=1, is_staff=1)
            user = authenticate(request, username=username, password="")
            if user is not None and user.is_active:
                dj_login(request, user)
                return redirect("/index")
            else:
                authorization_url = authenticate_ins.authorization_url
                full_url = "%s?client_id=%s&redirect_uri=%s" % (authorization_url, client_id, redirect_url)
                return HttpResponseRedirect(full_url)

    else:
        logger.error("incomplete parameters")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def update_authn(request):
    if request.method == 'POST':
        authenticate_tag = 0
        if request.POST.get("ldap") == "true":
            authenticate_tag = 1
        elif request.POST.get("oauth") == "true":
            authenticate_tag = 2
        authorization_url = request.POST.get("authorization_url")
        access_token_url = request.POST.get("access_token_url")
        client_id = request.POST.get("client_id")
        client_secret = request.POST.get("client_secret")
        redirect_url = request.POST.get("redirect_url")
        resource_url = request.POST.get("resource_url")
        grant_type = request.POST.get("grant_type")
        ldap_addr = request.POST.get("ldap_addr")
        dn_addr = request.POST.get("dn_addr")

        update_result = {"status": 0, "msg": "ok"}

        authenticate_ins = authenticate_type.objects.get(name="authentication")
        if authenticate_tag == 0:
            authenticate_ins.type = authenticate_tag
            authenticate_ins.save()
        elif authenticate_tag == 1:
            if ldap_addr and dn_addr:
                authenticate_ins.type = authenticate_tag
                authenticate_ins.authorization_url = ldap_addr
                authenticate_ins.access_token_url = ""
                authenticate_ins.client_id = ""
                authenticate_ins.client_secret = ""
                authenticate_ins.redirect_url = ""
                authenticate_ins.resource_url = dn_addr
                authenticate_ins.grant_type = ""
                authenticate_ins.save()
            else:
                update_result["status"] = 1
                update_result["msg"] = "请输入完整参数"
        elif authenticate_tag == 2:
            if authorization_url and access_token_url and client_id and client_secret and redirect_url and resource_url:
                authenticate_ins.type = authenticate_tag
                authenticate_ins.authorization_url = authorization_url
                authenticate_ins.access_token_url = access_token_url
                authenticate_ins.client_id = client_id
                authenticate_ins.client_secret = client_secret
                authenticate_ins.redirect_url = redirect_url
                authenticate_ins.resource_url = resource_url
                authenticate_ins.grant_type = grant_type
                authenticate_ins.save()
            else:
                update_result["status"] = 1
                update_result["msg"] = "请输入完整参数"

        return HttpResponse(json.dumps(update_result), content_type="application/json")

    if request.method == 'GET':
        authenticate_ins = authenticate_type.objects.get(name="authentication")

        authenticate_info = {
            "authenticate_tag": authenticate_ins.type,
            "authorization_url": authenticate_ins.authorization_url,
            "access_token_url": authenticate_ins.access_token_url,
            "client_id": authenticate_ins.client_id,
            "client_secret": authenticate_ins.client_secret,
            "redirect_url": authenticate_ins.redirect_url,
            "resource_url": authenticate_ins.resource_url,
            "grant_type": authenticate_ins.grant_type,

        }

        return HttpResponse(json.dumps(authenticate_info), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def upload_transfer_file(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            all_transfer_files = transfer_file.objects.all()
        else:
            all_transfer_files = transfer_file.objects.filter(user=User.objects.get(username=request.user)).all()
        return render(request, "transfer_file.html", {"all_transfer_files": all_transfer_files})

    upload_result = {"status": 0, "msg": "ok"}
    if request.method == 'POST':
        upload_file = request.FILES.get('file')
        dest_dir = request.POST.get('dest_dir')
        transfer_type = int(request.POST.get('transfer_type'))

        try:
            json.loads(dest_dir)
        except Exception as e:
            logger.error(traceback.format_exc())
            upload_result["status"] = 1
            upload_result["msg"] = "分发目录格式有错误: " + str(e)
            return HttpResponse(json.dumps(upload_result), content_type="application/json")

        if upload_file.size > int(settings.UPLOAD_FILE_SIZE) * 1024 * 1024:
            upload_result["status"] = 1
            upload_result["msg"] = "文件大小不能超过 %d MB, 请检查" %int(settings.UPLOAD_FILE_SIZE)
        else:
            if transfer_type == 0:
                try:
                    file_name = upload_file.name
                    file_name = ''.join(random.choices('0123456789', k=7)) + time.strftime(
                    "%Y%m%d%H%M%S", time.localtime())+'_'+file_name
                    with transaction.atomic():
                        transfer_file.objects.create(name=file_name, dest_dir=dest_dir, user=User.objects.get(username=request.user), type=0)

                        for each_sftp in salt_master.objects.filter(type=0).values("host", "sftp_port", "sftp_user", "sftp_password", "file_roots"):
                            sftp_storage = SFTPStorage(
                                host = each_sftp["host"].split("//")[1].split(":")[0],
                                root_path = each_sftp["file_roots"]+'/'+settings.SFTP_STORAGE_ROOT,
                                params ={
                                    'username': each_sftp["sftp_user"],
                                    'password': each_sftp["sftp_password"],
                                    'port': each_sftp["sftp_port"],
                                    'timeout': 60,
                                },
                                interactive = settings.SFTP_STORAGE_INTERACTIVE,

                            )
                            sftp_storage.save(file_name, upload_file)
                    upload_result["msg"] = "文件上传成功"

                except Exception as e:
                    logger.error(traceback.format_exc())
                    upload_result["status"] = 1
                    upload_result["msg"] = str(each_sftp["host"].split("//")[1].split(":")[0])+" SaltMaster主机上传文件发生异常: "+str(e)
            else:
                try:
                    file_name = upload_file.name
                    file_name = ''.join(random.choices('0123456789', k=7)) + time.strftime(
                        "%Y%m%d%H%M%S", time.localtime()) + '_' + file_name
                    with transaction.atomic():
                        transfer_file.objects.create(name=file_name, dest_dir=dest_dir,
                                                     user=User.objects.get(username=request.user), type=1)

                        for each_master in salt_master.objects.filter(type=1).values("file_roots"):
                            os.makedirs(each_master["file_roots"], exist_ok=True)
                            save_path = os.path.join(each_master["file_roots"], file_name)
                            with open(save_path, 'wb+') as save_file:
                                for chunk in upload_file.chunks():
                                    save_file.write(chunk)

                    upload_result["msg"] = "文件上传成功"

                except Exception as e:
                    logger.error(traceback.format_exc())
                    upload_result["status"] = 1
                    upload_result["msg"] = "Ansible主机上传文件发生异常: " + str(e)

        return HttpResponse(json.dumps(upload_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def delete_transfer_file(request):
    delete_result = {"status": 0, "msg": "ok"}

    file_id = request.POST.get("tf_id")
    transfer_file.objects.get(id=file_id).delete()
    return HttpResponse(json.dumps(delete_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def check_ldap(request):
    ldap_addr = request.POST.get("ldap_addr")
    dn_addr = request.POST.get("dn_addr")
    ldap_user = request.POST.get("ldap_user")
    ldap_passwd = request.POST.get("ldap_passwd")

    check_result = {"status": 0, "msg": "ok"}
    if ldap_addr and dn_addr and ldap_user and ldap_passwd:
        try:
            ldap_server = Server(ldap_addr, get_info=ALL, connect_timeout=10)
            user_dn = "uid=%s,%s" %(ldap_user, dn_addr)
            ldap_conn = Connection(ldap_server, user=user_dn, password=ldap_passwd, receive_timeout=10)

            if ldap_conn.bind():
                check_result["msg"] = "用户验证成功"
            else:
                check_result["msg"] = "用户验证失败"
        except Exception as e:
            logger.error(traceback.format_exc())
            check_result["status"] = 1
            check_result["msg"] = "用户验证异常, 请检查"

    else:
        check_result["status"] = 1
        check_result["msg"] = "请输入完整的验证信息"

    return HttpResponse(json.dumps(check_result), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def get_all_users(request):
    all_users = []
    for each_user in User.objects.all().values():
        all_users.append({"id": each_user["id"], "name": each_user["username"], "email": ""})
    return HttpResponse(json.dumps(all_users), content_type="application/json")

@login_required()
@audit_action
@csrf_exempt
def grant_st(request):
    st_id = request.POST.get("st_id")
    grant_users = request.POST.get("grant_users")

    grant_result = {"status": 0, "msg": "ok"}
    try:
        for each_user in json.loads(grant_users):
            with transaction.atomic():
                current_st = shell_template.objects.get(id=int(st_id))
                current_st.id = None
                current_st.name = current_st.name+"-"+each_user["name"]+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                current_st.user = User.objects.get(id=each_user["id"])
                current_st.save()
                if sub_template.objects.filter(name=shell_template.objects.get(id=int(st_id))):
                    for each_sub_st in sub_template.objects.filter(name=shell_template.objects.get(id=int(st_id))).values("id"):
                        current_sub_st = sub_template.objects.get(id=each_sub_st["id"])
                        current_sub_st.id = None
                        current_sub_st.name = current_st
                        current_sub_st.save()

    except Exception as e:
        logger.error(traceback.format_exc())
        grant_result["status"] = 1
        grant_result["msg"] = str(e)

    return HttpResponse(json.dumps(grant_result), content_type="application/json")