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
import os.path

from salt.common.audit_action import audit_action
from salt.common.permission_ctrl import superuser_required

import logging, json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, HttpResponse
from salt.models import *

# Create your views here.
logger = logging.getLogger("default")

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def list_masters(request):
    """
    展示所有ansible master简略信息
    :param request:
    :return:
    """
    all_masters = salt_master.objects.filter(type=1)
    return render(request, "an_masters.html", {"all_masters": all_masters})

@login_required()
@superuser_required
@audit_action
@csrf_exempt
def check_dir_perm(request):
    """
    检查分发文件路径可读写权限
    :param request:
    :return:
    """
    upload_dir = request.POST.get("input8")

    check_result = {"status": 0, "msg": "ok"}
    if not os.path.exists(upload_dir):
        check_result["status"] = 1
        check_result["msg"] = "分发文件路径不存在,请检查"
    elif os.access(upload_dir, os.R_OK) and os.access(upload_dir, os.W_OK):
        check_result["msg"] = "分发文件路径读写权限正常"
    else:
        check_result["status"] = 1
        check_result["msg"] = "分发文件路径读写权限异常,请检查"

    return HttpResponse(json.dumps(check_result), content_type="application/json")