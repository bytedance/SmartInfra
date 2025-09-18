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

import urllib.request
import urllib.parse
import json, ssl, logging, traceback

logger = logging.getLogger("default")

class SaltAPI():

    def __init__(self, url, user, passwd):
        self.__url = url
        self.__user = user
        self.__password = passwd
        self.__token_id = self.get_token()

    def get_token(self):
        """
        convert user/password to token_id
        :return:
        """
        try:
            params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
            obj = urllib.parse.urlencode(params).encode('utf-8')
            url = str(self.__url) + '/login'
            req = urllib.request.Request(url, obj)
            context = ssl._create_unverified_context()
            opener = urllib.request.urlopen(req, timeout=120, context=context)
            content = json.loads(opener.read())
            token_id = content['return'][0]['token']
        except Exception as e:
            logger.error(traceback.format_exc())
            token_id = None
        return token_id

    def send_req(self, data, prefix='/'):
        """
        send a request to the Salt Master
        :param data:
        :param prefix:
        :return:
        """
        url = str(self.__url) + prefix
        headers = {'X-Auth-Token': self.__token_id, 'Content-type': 'application/json'}
        context = ssl._create_unverified_context()
        try:
            data = bytes(json.dumps(data), 'utf8')
            req = urllib.request.Request(url, data, headers)
            opener = urllib.request.urlopen(req, timeout=120, context=context)
            content = json.loads(opener.read())
        except Exception as e:
            logger.error(traceback.format_exc())
            return str(e)
        return content

    def list_all_key(self):
        """
        list all keys
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.list_all', 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['return']}
        else:
            return {"status": 1, "msg": content}

    def delete_key(self, node_name):
        """
        delete the specified key
        :param node_name:
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['success']}
        else:
            return {"status": 1, "msg": content}

    def accept_key(self, node_name):
        """
        accept the specified key
        :param node_name:
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['success']}
        else:
            return {"status": 1, "msg": content}

    def reject_key(self, node_name):
        """
        reject the specified key
        :param node_name:
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.reject', 'match': node_name, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['success']}
        else:
            return {"status": 1, "msg": content}

    def execute_remote_shell(self, tgt, arg):
        """
        execute shell remotely
        :param tgt:
        :param arg:
        :param types:
        :return:
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'cmd.run', 'arg': arg, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            ret = content['return'][0]
            return {"status": 0, "msg": ret}
        else:
            return {"status": 1, "msg": content}

    def execute_grain(self, tgt, arg):
        """
        get the specified arg of one node
        :param tgt:
        :param arg:
        :return:
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.item', 'arg': arg, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]}
        else:
            return {"status": 1, "msg": content}

    def execute_grains(self, tgt):
        """
        get all args of one node
        :param tgt:
        :return:
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.items', 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]}
        else:
            return {"status": 1, "msg": content}

    def execute_remote_state(self, tgt, arg):
        """
        send a sls requests synchronously
        :param tgt:
        :param arg:
        :param types:
        :return:
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            ret = content.get("return")[0]
            return {"status": 0, "msg": ret}
        else:
            return {"status": 1, "msg": content}

    def runner_status(self, arg):
        """
        return all minions info
        :param arg:
        :return:
        """
        params = {'client': 'runner', 'fun': 'manage.' + arg, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            jid = content['return'][0]
            return {"status": 0, "msg": jid}
        else:
            return {"status": 1, "msg": content}

    def get_minion_status(self, node_name, arg):
        """
        return one minion info
        :param arg:
        :return:
        """
        params = {'client': 'runner', 'fun': 'manage.' + arg, 'tgt': node_name, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": 1, "message": content}

    def transfer_file(self, node_name, *args):
        """
        transfer file to some minions
        :param node_name:
        :param args:
        :return:
        """
        src_file = args[0]
        dest_file = args[1]
        params = {'client': 'local_async', 'fun': 'cp.get_file', 'tgt': node_name, 'arg': [src_file, dest_file]}
        content = self.send_req(params)
        if isinstance(content, dict):
            transfer_result = content['return'][0]
            return {"status": 0, "msg": transfer_result}
        else:
            return {"status": 1, "msg": content}

    def push_file(self, node_name, arg):
        """
        push file from one minion to master
        :param arg:
        :return:
        """
        params = {'client': 'local', 'fun': 'cp.push', 'tgt': node_name, 'arg': arg, 'timeout': 120}
        content = self.send_req(params)
        if isinstance(content, dict):
            push_result = content['return'][0]
            return {"status": 0, "msg": push_result}
        else:
            return {"status": 1, "msg": content}

