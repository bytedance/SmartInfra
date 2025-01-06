# -*- coding: UTF-8 -*-

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

