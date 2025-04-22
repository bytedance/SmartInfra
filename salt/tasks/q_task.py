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
import logging, datetime
from django_q.models import Task
from salt.models import task_list, User
from salt.common.notify_lark import create_lark_group

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
        task_list.objects.filter(id=task_result.kwargs["new_task_id"]).update(status=2, update_time=datetime.datetime.now(), execute_result=str(task_result.result))

        # send message to current user
        task_info = task_list.objects.get(id=task_result.kwargs["new_task_id"])
        create_lark_group(group_name=task_info.name, current_user=User.objects.get(id=task_info.user_id).username)
