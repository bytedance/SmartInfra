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

import datetime
import logging, traceback, time
from salt.models import salt_master, hosts
from salt.common.salt_api import SaltAPI
from django_q.models import Task

# Create your views here.
logger = logging.getLogger("default")


def register_hosts():
    all_salt_master = list(salt_master.objects.all().values("id", "host", "user", "password"))
    reg_result = {"status": 0, "msg": "ok"}
    update_label = time.strftime("%m%d%H%M%S", time.localtime())

    if not all_salt_master:
        reg_result["status"]=1
        reg_result["msg"]="无有效的Salt Master资源"
        return reg_result

    try:
        Task.objects.filter(id="refresh_label").update(success=1, started=datetime.datetime.now())
        for each_salt_master in all_salt_master:
            salt_ins = SaltAPI(each_salt_master["host"], each_salt_master["user"], each_salt_master["password"])
            if salt_ins.get_token() is None:
                logger.error("Salt Master %s 无法有效连接" %each_salt_master["host"])
            else:
                all_minions = salt_ins.runner_status("status")
                minion_up = all_minions["msg"]["up"]
                minion_down = all_minions["msg"]["down"]
                all_keys = salt_ins.list_all_key()
                for each_minion in all_keys["msg"]["minions"]:
                    if each_minion in minion_up:
                        minion_status = 0
                    elif each_minion in minion_down:
                        minion_status = 1
                    else:
                        minion_status = 2
                    accepted_minion = hosts.objects.filter(name=each_minion, status=minion_status, salt=salt_master.objects.get(id=each_salt_master["id"])).first()
                    if accepted_minion:
                        accepted_minion.label=update_label
                        accepted_minion.save()
                    else:
                        hosts.objects.create(name=each_minion, status=minion_status,
                                             salt=salt_master.objects.get(id=each_salt_master["id"]), label=update_label)

                for abnormal_status in ["minions_pre", "minions_rejected", "minions_denied"]:
                    host_status_choices = {"minions_pre":3, "minions_denied":4, "minions_rejected":5}
                    for each_abnormal in all_keys["msg"][abnormal_status]:
                        abnormal_minion = hosts.objects.filter(name=each_abnormal, status=host_status_choices[abnormal_status], salt=salt_master.objects.get(id=each_salt_master["id"])).first()
                        if abnormal_minion:
                            abnormal_minion.label=update_label
                            abnormal_minion.save()
                        else:
                            hosts.objects.create(name=each_abnormal, status=host_status_choices[abnormal_status],
                                                 salt=salt_master.objects.get(id=each_salt_master["id"]), label=update_label)

                hosts.objects.exclude(label=update_label).delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        reg_result["status"]=1
        reg_result["msg"]=str(e)

    return reg_result
