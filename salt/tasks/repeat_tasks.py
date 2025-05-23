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
