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

from salt.models import acl_manage
import traceback, logging

logger = logging.getLogger("default")

def parse_content(shell_content):
    if not shell_content:
        return {"status": 1, "msg": "invalid input"}

    try:
        allow_shell_content = acl_manage.objects.get(name='acl').content.split()

        # replace matched char
        to_replace_charactor1 = ["&", "|"]
        for index, each_charactor1 in enumerate(to_replace_charactor1):
            if each_charactor1 in shell_content:
                shell_content = shell_content.replace(each_charactor1, " ")

        # remove matched arg
        to_replace_charactor2 = ["/", "-"]
        shell_content = shell_content.split()
        for each_charactor2 in to_replace_charactor2:
            for each_sc in shell_content:
                if each_charactor2 in each_sc:
                    shell_content.remove(each_sc)
        shell_content = " ".join(_ for _ in shell_content)

        # start to match between shell_content and allow_shell_content
        for each_shell_content in shell_content.split():
            if each_shell_content not in allow_shell_content:
                return {"status": 1, "msg": "rw"}

        return {"status": 0, "msg": "ro"}
    except Exception as e:
        logger.error(traceback.format_exc())
        return {"status": 1, "msg": str(e)}

