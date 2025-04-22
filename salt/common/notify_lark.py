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

import traceback
import requests, json
from salt.models import authenticate_type
import logging

logger = logging.getLogger("default")

def create_lark_group(group_name, current_user):
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
            new_user_id_list = []
            current_user_id = ""
            for each_user_id in user_id_list:
                if each_user_id["email"] == current_user+"@bytedance.com":
                    current_user_id = each_user_id["user_id"]
                new_user_id_list.append(each_user_id["user_id"])
            create_group_data = {
                "name": "SmartInfra平台工单任务状态变化通知",
                "user_id_list": new_user_id_list,
            }
            create_group_raw = requests.post("https://open.larkoffice.com/open-apis/im/v1/chats", json=create_group_data, headers=auth_common_headers,
                               timeout=10)
            if json.loads(create_group_raw.content)["code"] == 0:
                chat_id = json.loads(create_group_raw.content)["data"]["chat_id"]
            else:
                logger.info("some errors occurs when trying to create a group")
                return

            # send message to current user
            send_message_data = {
                "receive_id": chat_id,
                "msg_type": "text",
                "content": "{\"text\":\"<at user_id=\\\"%s\\\">用户名</at> 您发起的任务 - %s - 已执行完成，请及时检查结果！\"}" %(current_user_id, group_name)
            }
            send_message_raw = requests.post("https://open.larkoffice.com/open-apis/im/v1/messages?receive_id_type=chat_id",
                                    json=send_message_data, headers=auth_common_headers, timeout=10)
            logger.info(send_message_raw.content)

        except Exception as e:
            logger.error(traceback.format_exc())

    else:
        logger.info("The platform does not support by Lark right now")
