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

import json

from salt.models import task_list
from django_q.models import Schedule
import logging, traceback


logger = logging.getLogger("default")

def create_repeat_task(old_id):
    """
    创建一个新的重复任务
    :param old_id:
    :return:
    """
    try:
        repeat_task = task_list.objects.get(id=old_id)
        if Schedule.objects.get(id=repeat_task.related_schedule).repeats == 0:
            logger.info("定时任务执行次数结束，不再创建新的任务列表")
            return
        repeat_task.id = None
        repeat_task.status = 1
        repeat_task.save()
        new_kwargs = json.dumps({"new_task_id": repeat_task.id})
        Schedule.objects.filter(id=repeat_task.related_schedule).update(kwargs=new_kwargs)
    except Exception as e:
        logger.error(traceback.format_exc())
