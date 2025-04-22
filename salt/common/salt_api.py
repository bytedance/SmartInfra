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
            opener = urllib.request.urlopen(req, timeout=10, context=context)
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
            opener = urllib.request.urlopen(req, timeout=60, context=context)
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
        params = {'client': 'wheel', 'fun': 'key.list_all'}
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
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
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
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
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
        params = {'client': 'wheel', 'fun': 'key.reject', 'match': node_name}
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
        params = {'client': 'local', 'tgt': tgt, 'fun': 'cmd.run', 'arg': arg}
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
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.item', 'arg': arg}
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
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.items'}
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
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
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
        params = {'client': 'runner', 'fun': 'manage.' + arg}
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
        params = {'client': 'runner', 'fun': 'manage.' + arg, 'tgt': node_name}
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
        params = {'client': 'local', 'fun': 'cp.push', 'tgt': node_name, 'arg': arg}
        content = self.send_req(params)
        if isinstance(content, dict):
            push_result = content['return'][0]
            return {"status": 0, "msg": push_result}
        else:
            return {"status": 1, "msg": content}

