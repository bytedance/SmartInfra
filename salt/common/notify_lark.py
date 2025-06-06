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

import traceback
import requests, json
from datetime import datetime
from decouple import config
from salt.models import authenticate_type, chat_group, User
import logging

logger = logging.getLogger("default")

def send_lark_msg(task_name, current_user, message):
    authenticate_ins = authenticate_type.objects.get(name="authentication")

    if authenticate_ins.client_id and authenticate_ins.client_secret:
        try:
            # get lark authentication
            tenant_access_token_data = {"app_id": authenticate_ins.client_id, "app_secret": authenticate_ins.client_secret}
            tenant_access_token_headers = {"Content-Type": "application/json; charset=utf-8"}
            tenant_access_token_raw = requests.post("https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal", json=tenant_access_token_data, headers=tenant_access_token_headers, timeout=10)
            tenant_access_token = json.loads(tenant_access_token_raw.content)["tenant_access_token"]

            # organize the headers
            auth_common_headers = {"Authorization": "Bearer %s" %tenant_access_token, "Content-Type": "application/json; charset=utf-8"}

            # get user id according to email
            user_id_data = {
                "emails": [
                    "luwanlong@bytedance.com",
                    current_user+"@bytedance.com",
                ],
            }
            user_id_raw = requests.post("https://open.larkoffice.com/open-apis/contact/v3/users/batch_get_id", json=user_id_data,
                               headers=auth_common_headers, timeout=10)
            if json.loads(user_id_raw.content)["code"] == 0:
                user_id_list = json.loads(user_id_raw.content)["data"]["user_list"]
            else:
                logger.info("some errors occurs when trying to get user_id")
                return

            # create a chat group
            cg_ins = chat_group.objects.filter(user=User.objects.get(username=current_user))
            new_user_id_list = []
            current_user_id = ""
            for each_user_id in user_id_list:
                if each_user_id["email"] == current_user + "@bytedance.com":
                    current_user_id = each_user_id["user_id"]
                new_user_id_list.append(each_user_id["user_id"])

            if cg_ins:
                chat_id = cg_ins.values("chat_id").first()["chat_id"]
            else:
                create_group_data = {
                    "name": "SmartInfra平台工单任务状态变化通知",
                    "user_id_list": new_user_id_list,
                }
                create_group_raw = requests.post("https://open.larkoffice.com/open-apis/im/v1/chats", json=create_group_data, headers=auth_common_headers,
                                   timeout=10)
                if json.loads(create_group_raw.content)["code"] == 0:
                    chat_id = json.loads(create_group_raw.content)["data"]["chat_id"]
                    chat_group.objects.create(user=User.objects.get(username=current_user), chat_id=chat_id)
                else:
                    logger.info("some errors occurs when trying to create a group")
                    return

            # send message to current user
            send_message_data = {
                "receive_id": chat_id,
                "msg_type": "interactive",
                "content": "{\"type\":\"template\",\"data\":{\"template_id\":\"%s\",\"template_version_name\":\"1.0.0\",\"template_variable\":{\"task_name\":\"%s\",\"task_status\":\"%s\",\"open_id\":\"%s\",\"complete_time\":\"%s\"}}}"
                           % (config('TEMPLATE_ID'), task_name, message, current_user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
            send_message_raw = requests.post("https://open.larkoffice.com/open-apis/im/v1/messages?receive_id_type=chat_id",
                                    json=send_message_data, headers=auth_common_headers, timeout=10)
            logger.info(send_message_raw.content)

        except Exception as e:
            logger.error(traceback.format_exc())

    else:
        logger.info("The platform does not support by Lark right now")
