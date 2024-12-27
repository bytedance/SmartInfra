import datetime
import json
from datetime import timezone, datetime

import time

from django.test import TestCase

# Create your tests here.
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

"""
url = "https://10.0.77.41:8888/"
user = "saltapi"
password = "salt2022@ByteDance"
"""




#
# next_run_time = []
# rr = "20 * 9 * *"
# if rr.split()[0] == "*":
#     next_run_time.append(0)
# else:
#     next_run_time.append(rr.split()[0])
#
# if rr.split()[1] == "*":
#     if int(next_run_time[0])<int(datetime.datetime.now().strftime("%M")):
#
#         next_run_time.append(int(datetime.datetime.now().strftime("%H"))+1)
#     else:
#         next_run_time.append(datetime.datetime.now().strftime("%H"))
# else:
#     next_run_time.append(rr.split()[1])
#
# if rr.split()[2] == "*":
#     if int(next_run_time[1])<int(datetime.datetime.now().strftime("%H")):
#         next_run_time.append(int(datetime.datetime.now().strftime("%d"))+1)
#     else:
#
#         next_run_time.append(datetime.datetime.now().strftime("%d"))
# else:
#     next_run_time.append(rr.split()[2])
#
# if rr.split()[3] == "*":
#     if int(next_run_time[2])<int(datetime.datetime.now().strftime("%d")):
#         next_run_time.append(int(datetime.datetime.now().strftime("%m"))+1)
#     else:
#         next_run_time.append(datetime.datetime.now().strftime("%m"))
# else:
#     next_run_time.append(rr.split()[3])
#
# next_run_time.append(datetime.datetime.now().strftime("%Y"))
# print(next_run_time)

from common.salt_api import SaltAPI

sa=SaltAPI(url="https://10.0.77.41:8888/", user="saltapi", passwd="salt2022@ByteDance")
# print(datetime.datetime.now())
# # time.sleep(60)
# print(datetime.datetime.now())

iiii = "ls /tmp"
uuuu = "/tmp/5566"
# xx = sa.execute_remote_state("10.0.85.141-www111", "smartinfra/admin-000000-2024122444444")
# xx = sa.execute_remote_shell("10.0.85.141-www111", "echo %s > %s" %(iiii, uuuu))
# yy = sa.push1_file("10.0.85.141-www111", "salt://smartinfra", "/etc/gai.conf")

# xx = sa.push_file("10.0.85.141-www111", "/etc/adduser.conf")
# print(xx["msg"])
# print(yy)
# key = "100.94.64.2-CNDAT06-F09-M-R450-GW01"
# value1 = xx["msg"][key]
# with open("111.txt", 'a+', encoding="utf-8") as ersrf:
#     ersrf.write(f"{key}:\n{value1}\n" + '\n')
# import random
# print(type(''.join(random.choices('0123456789', k=7))))
#
# xxxxx=['q',"eeee","23333"]
# print(str(xxxxx))

# data = {
#     '100.94.64.2-CNDAT06-F09-M-R450-GW01': '_MEII4rDoZ\ngolang-dnstap-formater.deb\ngolang-sync-ipset.deb\ngw\nnamespace-dev-3meAvs\nnamespace-dev-5TNmaD\nnamespace-dev-6LmP8a\nnamespace-dev-B6obUK\nnamespace-dev-DkDgzp\nnamespace-dev-TUytCC\nnamespace-dev-Y4x1gK\nnamespace-dev-YCp18Z\nnamespace-dev-cajysC\nnamespace-dev-dh8R5D\nnamespace-dev-uxXaZk\nnamespace-dev-vEDSNZ\nnamespace-dev-z0bl77\nsystemd-private-c5eacfa6f96f44d2a8c57a1933ee2a53-dnsdist.service-mghpvj\nsystemd-private-c5eacfa6f96f44d2a8c57a1933ee2a53-lldpd.service-pl6HZh\nsystemd-private-c5eacfa6f96f44d2a8c57a1933ee2a53-pdns-recursor.service-AIlWNf\nzabbix_agent2.log'
# }
# print(type(xx["msg"]))
# # 提取键值对，并将值中的换行符 `\n` 生效
# key = list(xx["msg"].keys())[0]
# value = data[key]
#
# # 写入文件
# with open("output.txt", "w", encoding="utf-8") as file:
#     file.write(f"{key}:\n{value}\n")

#
import os
import sys
import django


# 添加项目根目录到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
print(PROJECT_ROOT)

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartinfra.settings')

django.setup()

sa=SaltAPI(url="https://10.0.77.41:8888/", user="saltapi", passwd="salt2022@ByteDance")
# print(datetime.datetime.now())
# # time.sleep(60)
# print(datetime.datetime.now())
from salt.models import shell_template, task_list
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.db.models import Sum

st_info = shell_template.objects.get(id=14)
main_content = st_info.func_content
print(main_content.replace('"', '\\"').replace('$', '\$'))
# cc = 'echo "%s" > %s' %(main_content.replace('"', '\\"'), uuuu)
# print(cc)
iiii = "\r"
uuuu = "/tmp/1122334"
each_minion = "10.0.85.53-luwanlong"
# yy = sa.execute_remote_state("10.0.85.53-luwanlong", "smartinfra_state/admin300102820241213074707")
# import base64
# main_content = base64.b64encode(main_content.encode()).decode()
# print(main_content)
# yy = sa.execute_remote_shell("10.0.85.141-www111", 'echo "%s" > %s' %(main_content, uuuu))
# xx = sa.execute_remote_shell("10.0.85.141-www111", 'base64 --decode /tmp/1122334 > /tmp/11223345')
# print(yy)
# xx = sa.execute_remote_shell("10.0.85.141-www111", 'cat /etc/passwd')
# print(str(yy['msg'][each_minion]))
# print(xx)

# with open("xxxxx.log", 'a+', encoding="utf-8") as ersrf:
#     # 替换掉 \r，并确保使用统一的换行符 \n
#     cleaned_content = str(yy['msg'][each_minion]).replace('\\r\\n', '\n')
#     # ui = "\\r\\n"
#     # if ui in cleaned_content:
#     print(cleaned_content)
#     # 写入文件，确保每个内容后面只有一个换行符
#     ersrf.write(f"{each_minion}:\n{cleaned_content}\n")
# end_date = datetime.now()
# start_date = end_date - timedelta(days=7)
#
# # 查询最近7天的数据，按用户分组统计行数
# data = (
#     task_list.objects.filter(create_time__date__range=[start_date.date(), end_date.date()])
#     .values('user_id')  # 按用户分组
#     .annotate(count=Count('id'))  # 统计每个用户的行数
#     .order_by('user_id')  # 按用户 ID 排序（可选）
# )
#
# # 转换为字典形式 {user_id: count}
# result_dict = {item['user_id']: item['count'] for item in data}
#
# print(result_dict)
# import requests
# cc = requests.get("https://accounts.feishu.cn/open-apis/authen/v1/authorize?client_id=cli_a7e0a93868b0d013&redirect_uri=http://172.16.227.129:8080/&&state=12345687")
# print(cc.url)
from salt.models import hosts
include_salt = [17]
all_minions = hosts.objects.filter(salt__in=include_salt, status=0).values("name")
print(all_minions)