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
import ast
import logging, datetime
from django_q.models import Task
from salt.models import task_list, User
from salt.common.notify_lark import send_lark_msg

# Create your views here.
logger = logging.getLogger("default")

def running_task(task_result):
    """
    刷新任务执行完成后，更新状态
    :return:
    """
    logger.info(task_result)
    Task.objects.filter(id="refresh_label").update(success=0, stopped=datetime.datetime.now())

def remote_shell_task(task_result):
    """
    执行命令任务执行完成后，更新状态
    :return:
    """
    if task_result.success:
        if task_list.objects.get(id=task_result.kwargs["new_task_id"]).status == 6:
            task_status = 6
        else:
            task_status = 2
        task_list.objects.filter(id=task_result.kwargs["new_task_id"]).update(status=task_status, update_time=datetime.datetime.now(), execute_result=str(task_result.result))

        # send message to current user
        task_info = task_list.objects.get(id=task_result.kwargs["new_task_id"])
        display_result = ast.literal_eval(task_info.execute_result)
        send_lark_msg(task_name=task_info.name, current_user=User.objects.get(id=task_info.user_id).username,
                      message="已执行完成, 执行结果{'成功数量': %d, '失败数量': %d}, 请及时登录[SmartInfra平台](%s)检查结果"
                              %(display_result["count_success"], display_result["count_fail"], task_result.kwargs["custom_url"]))
