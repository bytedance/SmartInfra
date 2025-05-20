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