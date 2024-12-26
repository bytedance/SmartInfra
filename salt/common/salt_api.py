# -*- coding: UTF-8 -*-

import urllib.request
import urllib.parse
import json, ssl, logging

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
            logger.error(e)
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
            logger.error(e)
            return str(e)
        return content

    def list_all_key(self):
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['return']}
        else:
            return {"status": 1, "msg": content}

    def delete_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['success']}
        else:
            return {"status": 1, "msg": content}

    def accept_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]['data']['success']}
        else:
            return {"status": 1, "msg": content}

    def reject_key(self, node_name):
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
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.item', 'arg': arg}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]}
        else:
            return {"status": 1, "msg": content}

    def execute_grains(self, tgt):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.items'}
        content = self.send_req(params)
        if isinstance(content, dict):
            return {"status": 0, "msg": content['return'][0]}
        else:
            return {"status": 1, "msg": content}

    # def target_remote_execution(self, tgt, fun, arg):
    #     # Use targeting for remote execution
    #     params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'nodegroup'}
    #     content = self.send_req(params)
    #     if isinstance(content, dict):
    #         jid = content['return'][0]['jid']
    #         return jid
    #     else:
    #         return {"status": False, "message": "Salt API Error : " + content}

    # def execute_deploy(self, tgt, arg):
    #     # Module deployment
    #     params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
    #     return self.send_req(params)
    #
    # def execute_async_deploy(self, tgt, arg):
    #     """
    #     send a sls request asynchronously, and return a job id
    #     :param tgt:
    #     :param arg:
    #     :return:
    #     """
    #     params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
    #     content = self.send_req(params)
    #     if isinstance(content, dict):
    #         return content['return'][0]['jid']
    #     else:
    #         return {"status": 1, "message": content}

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

    def get_jobs_list(self):
        url = self.__url + '/jobs/'
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        context = ssl._create_unverified_context()
        try:
            opener = urllib.request.urlopen(req, context=context)
            content = json.loads(opener.read())
        except Exception as e:
            logger.error(e)
            return str(e)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": 1, "message": content}

    def get_job_info(self, arg):
        url = self.__url + '/jobs/' + arg
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        context = ssl._create_unverified_context()
        try:
            opener = urllib.request.urlopen(req, context=context)
            content = json.loads(opener.read())
        except Exception as e:
            logger.error(e)
            return str(e)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": 1, "message": content}

    def get_stats(self):
        """
        expose statistics about the running CherryPy server
        :return:
        """
        url = self.__url + '/stats'
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        context = ssl._create_unverified_context()
        try:
            opener = urllib.request.urlopen(req, context=context)
            content = json.loads(opener.read())
        except Exception as e:
            logger.error(e)
            return str(e)
        if isinstance(content, dict):
            return content
        else:
            return {"status": 1, "message": content}

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
        params = {'client': 'local', 'fun': 'cp.get_file', 'tgt': node_name, 'arg': [src_file, dest_file]}
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

