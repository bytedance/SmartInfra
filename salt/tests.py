import datetime
import json
from datetime import timezone, datetime
from encodings.utf_7 import encode

import time

from django.test import TestCase

# Create your tests here.
from pathlib import Path

from ansible.tests import pb_hosts_dir

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
yy = sa.transfer_file("10.0.85.53-luwanlong", "salt://smartinfra/111", "C:\\Users")
print(yy)
# print(sa.get_job_info("20250103111256682314"))
# if sa.get_job_info("20250103111256682314")["msg"]:
#     print(1111)
# else:
#     print(22222)
# host = "10.0.87.225-useroptvm"
# print(sa.execute_grains(host)["msg"][host]["kernel"])
# if isinstance(sa.execute_grains(host)["msg"][host], dict):
#     print(sa.execute_grains(host)["msg"][host])
# else:
#     print(1111111)
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
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
print("############")
print(PROJECT_ROOT)

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartinfra.settings')

django.setup()

from salt.models import host_group, host_group_minion
# import requests
#
# uu = "https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal"
# app_id="cli_a7e0a93868b0d013"
# app_secret="yKFKimNkXih9WCi9ClQ4ycS87IeV51ja"
#
# tenant_token_data = {"app_id": app_id, "app_secret": app_secret}
# tenant_headers = {"Content-Type": "application/json; charset=utf-8"}
# response_content = requests.post(uu, json=tenant_token_data, headers=tenant_headers, timeout=10)
# print(json.loads(response_content.content))
#
# token = {"Authorization": "Bearer t-g1044livRNOTCY236NELHGPEWDYSKYZRKMAOXCP4", "Content-Type": "application/json; charset=utf-8"}
#
# get_ou = {
#   "emails": [
#     "luwanlong@bytedance.com",
#       "zhangliangliang@bytedance.com"
#   ],
# }
# yy = requests.post("https://open.larkoffice.com/open-apis/contact/v3/users/batch_get_id", json=get_ou, headers=token, timeout=10)
# print(json.loads(yy.content))
#
# create_token_data = {
#   "name": "测试群名称",
#   "user_id_list": [
#     "ou_c47b00930497cfa5f026e06c2abeabda"
#   ],
# }
# create_headers = {"Authorization": token, "Content-Type": "application/json; charset=utf-8"}
# xx = requests.post("https://open.larkoffice.com/open-apis/im/v1/chats", json=create_token_data, headers=token, timeout=10)
# print(json.loads(xx.content))
#
# send_data = {
#     "receive_id": "oc_d9a75d636e9017f359835999d0a60383",
#     "msg_type": "text",
#     "content": "{\"text\":\"<at user_id=\\\"ou_c47b00930497cfa5f026e06c2abeabda\\\">用户名</at> 欢迎加入群聊！\"}"
# }
#
# zz = xx = requests.post("https://open.larkoffice.com/open-apis/im/v1/messages?receive_id_type=chat_id", json=send_data, headers=token, timeout=10)
from salt.models import User, task_list
task_info = task_list.objects.get(id=338)
print(type(User.objects.get(id=task_info.user_id).username))


# sa=SaltAPI(url="https://10.0.77.41:8888/", user="saltapi", passwd="salt2022@ByteDance")
# # print(datetime.datetime.now())
# # # time.sleep(60)
# # print(datetime.datetime.now())
# from salt.models import shell_template, task_list, transfer_file
# from datetime import timedelta
# from django.db.models.functions import TruncDate
# from django.db.models import Sum
#
# st_info = shell_template.objects.get(id=14)
# main_content = st_info.func_content
# print(main_content.replace('"', '\\"').replace('$', '\$'))
# # cc = 'echo "%s" > %s' %(main_content.replace('"', '\\"'), uuuu)
# # print(cc)
# iiii = "\r"
# uuuu = "/tmp/1122334"
# each_minion = "10.0.85.53-luwanlong"
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
#host_group_id, transfer_file_id, current_user
# print(result_dict)
# import requests
# cc = requests.get("https://accounts.feishu.cn/open-apis/authen/v1/authorize?client_id=cli_a7e0a93868b0d013&redirect_uri=http://172.16.227.129:8080/&&state=12345687")
# print(cc.url)
# from salt.models import hosts, salt_master
# each_minion = "10.0.85.53-luwanlong"
# salt_server = salt_master.objects.get(id=(hosts.objects.get(name=each_minion)).salt_id)
# s2 = salt_master.objects.get(id=hosts.objects.filter(name=each_minion).values("salt_id").first()["salt_id"])
# print(salt_server)
# print(s2)
# print(hosts.objects.filter(name=each_minion).values("salt_id").first())

# from salt.tasks.exec_task import exec_transfer_file
#
# host_group_id=42
# transfer_file_id=17
# current_user='admin'
# xx1 = exec_transfer_file(host_group_id, transfer_file_id, current_user, new_task_id=159)
# print(xx1)
# input_email = "luwanlong"
# resource_url = "ou=users,dc=sqlpara,dc=com"
# user_dn = "uid=%s,%s" %(input_email, resource_url)
# print(user_dn)
#
# from ldap3 import Server, Connection, ALL
# ldap_server = Server("ldap://10.66.17.84:389", get_info=ALL)
# ldap_conn = Connection(ldap_server, user="uid=john,ou=users,dc=sqlpara,dc=com", password="johnspassword")
#
# if ldap_conn.bind():
#     print("1111")
# else:
#     print("22222")

import requests

data = {
    "AppID": "smartsalt",
    "AppSecret": "fc3cb27d-f8d0-11ef-a045-00163e1deea0"
}
url = "https://glata-staging.bytedance.net/open/v2/access_token"
cc = requests.post(url=url, data=data)
print(cc.json()["AccessToken"])

create_header = {
    "x-glata-open-access-token": cc.json()["AccessToken"],
    "x-tt-env" : "ppe_cn_env_mri",
    "x-use-ppe": "1"
}

create_data = {
    "NamespaceId": 1,
    "ProjectId": 1,
    "TypeId": 246,
    "Creator": "luwanlong@bytedance.com",
    "SystemFields": {
        "Title": "task_name",
        "PriorityId": "P-3",
        "Reporter": "luwanlong@bytedance.com",
        "Assignee": "luwanlong@bytedance.com",
        "SourceId": 0,
        "Location": "All POPs",
        "Description": "来自smartsalt的自动化变更"
    },
    "CustomFields": {
        "change_type": "Standard",
        "change_risk": "P3 (Low)",
        "risk_assessment": "",
        "scheduled_start_time": 1734009606000,
        "scheduled_end_time": 1734009966000,
        "deployment_plan": "部署计划",
        "validation_plan": "验证计划",
        "rollback_plan": "回滚计划",
        "outage_needed": "否",
        "onsite_support_needed": "否",
        "testing_staging_environment": "通过",
        "single_line_text_1706845354": "",
        "dropdown_radio_1715929318": "",
        "multi_user_selector_1704785697": [

        ],
        "technicalCatalogId": 583
    },
    "AutoCompleteFields": {
        "site_itmd_code": [
            "ITBD00000243"
        ],
        "site_code": "site_code",
        "business_line": "business_line",
        "scheduled_hours_worked": "scheduled_hours_worked",
        "change_manager": "change_manager",
        "tech_approver": "tech_approver"
    }
}
create_url = "https://glata-staging.bytedance.net/open/v2/ticket"

# dd = requests.post(url=create_url, json=create_data, headers=create_header)
# print(dd.json())
from zoneinfo import ZoneInfo
import datetime

print(datetime.datetime.now())
time_format = "%Y-%m-%d %H:%M:%S.%f"
utc_time = datetime.datetime.strptime(str(datetime.datetime.now()), time_format).replace(tzinfo=ZoneInfo('UTC'))
cst_time = utc_time.astimezone(ZoneInfo('Asia/Shanghai'))
cst_timestamp = cst_time.timestamp()
actual_end_time = int(cst_timestamp)*1000
print(actual_end_time)
ticket_seq = 152902701
update_header = {
    "x-glata-open-access-token": cc.json()["AccessToken"],
    "x-tt-env": "ppe_cn_env_mri",
    "x-use-ppe": "1"
}
update_data = {
    "TicketSeq": ticket_seq,
    "ProjectId": 1,
    "ActionNode": "1_1_action_1704822469127_2404",
    "CustomFields": {
        "change_result": 1,
        "actual_end_time": actual_end_time
    }
}
update_url = "https://glata-staging.bytedance.net/open/v2/ticket/transit"
rr = requests.post(url=update_url, json=update_data, headers=update_header)
print(rr.content)
# check_header = {
#    "x-glata-open-access-token": cc.json()["AccessToken"],
#    "x-tt-env" : "ppe_cn_env_mri",
#    "x-use-ppe": "1"
# }
#
# check_data = {
#     "Seq": "152180808"
# }
#
# ee=requests.get(url="https://glata-staging.bytedance.net/open/v2/ticket", headers=check_header, json=check_data)
# print(ee.json())

