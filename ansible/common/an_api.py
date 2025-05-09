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

import ansible_runner, logging, json

logger = logging.getLogger("default")

class AnsibleAPI():

    def __init__(self, private_data_dir, login_key_dir):
        self.private_data_dir = private_data_dir
        self.login_key = login_key_dir
        self.last_event = None
        self.log_lines = []

    def handle_event(self, event):
        """
        catch the last event
        :param event:
        :return:
        """
        self.last_event = event
        stdout_line = event.get('stdout')
        if stdout_line:
            self.log_lines.append("[STDOUT] {}\n".format(stdout_line))

        res = event.get('event_data', {}).get('res', {})
        res_stdout = res.get('stdout')
        if res_stdout:
            self.log_lines.append("[RES_STDOUT] {}\n".format(res_stdout))
        elif res:
            res_pretty = json.dumps(res, ensure_ascii=False, indent=2)
            self.log_lines.append("[RES_OBJECT]\n")
            for line in res_pretty.splitlines():
                self.log_lines.append("    " + line + "\n")

        res_stderr = res.get('stderr')
        if res_stderr:
            self.log_lines.append("[RES_STDERR] {}\n".format(res_stderr))

    def run_command(self, module, arg):
        """
        run a shell
        :param module:
        :param arg:
        :return:
        """
        r_content = ansible_runner.run(
            private_data_dir=self.private_data_dir,
            module=module,
            module_args=arg,
            host_pattern='all',
            event_handler=self.handle_event,
            forks=10,
            envvars={
                'ANSIBLE_PRIVATE_KEY_FILE': self.login_key,
                'ANSIBLE_CONNECTION_TIMEOUT': 5
            }
        )
        return r_content

    def run_playbook(self, pb_name):
        """
        run a playbook
        :param pb_name:
        :return:
        """
        r_content = ansible_runner.run(
            private_data_dir=self.private_data_dir,
            playbook=pb_name,
            event_handler=self.handle_event,
            forks=10,
            envvars={
                'ANSIBLE_PRIVATE_KEY_FILE': self.login_key,
                'ANSIBLE_CONNECTION_TIMEOUT': 5
            }
        )
        return r_content

    def transfer_file(self, module, arg):
        """
        transfer file to some nodes
        :param module:
        :param arg:
        :return:
        """
        r_content = ansible_runner.run(
            private_data_dir=self.private_data_dir,
            module=module,
            module_args=arg,
            host_pattern='all',
            event_handler=self.handle_event,
            forks=10,
            envvars={
                'ANSIBLE_PRIVATE_KEY_FILE': self.login_key,
                'ANSIBLE_CONNECTION_TIMEOUT': 5
            }
        )
        return r_content


