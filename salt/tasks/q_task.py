# -*- coding: UTF-8 -*-

import logging, datetime
from django_q.models import Task
from salt.models import task_list

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
