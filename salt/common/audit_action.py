# -*- coding: UTF-8 -*-

from salt.models import general_audit
import logging
from functools import wraps

logger = logging.getLogger("default")

def audit_action(func):
    URL_DESCRIPTIONS = {
        'index': '显示主页内容',
        'login': '用户登录',
        'logout_user': '用户退出',
        'authenticate_user': '用户认证',
        'salt_masters': '查看所有SaltMaster',
        'create_salt': '创建/修改新的SaltMaster',
        'del_salt': '删除已纳管的SaltMaster',
        'check_salt_master': '检查SaltMaster是否正常',
        'check_sftp': '检查SFTP是否正常',
        'shell_template': '查看所有执行模板',
        'create_shell_template': '创建/修改执行模板',
        'del_shell_template': '删除执行模板',
        'resource_group': '查看所有资源组',
        'create_resource_group': '创建/修改资源组',
        'del_resource_group': '删除资源组',
        'ro_setup': '查看所有只读命令',
        'create_acl': '更新只读命令',
        'users_list': '查看所有用户',
        'create_user_relationship': '创建/修改用户关联资源',
        'del_user': '删除用户',
        'hosts': '查看所有被纳管的主机',
        'setup_host': '配置主机，接受、删除和拒绝',
        'refresh_minion': '重新发现被纳管主机',
        'read_file': '读取主机组上传文件内容',
        'host_group': '查看所有主机组',
        'create_host_group': '创建/修改主机组',
        'download_hg': '下载匹配失败的主机详细信息',
        'del_host_group': '删除主机组',
        'show_selected_host_group': '查看已选主机组',
        'search_available_host': '查看当前用户可操作主机',
        'create_shell_task': '创建/修改执行任务',
        'list_tasks': '查看所有已创建任务信息',
        'approve_task': '审批任务',
        'get_task_info': '获取任务信息',
        'download_execute_result': '下载已执行完成任务结果',
        'show_message': '查看待审批任务信息',
        'audit_info': '查看审计信息条目',
        'authenticate_mgmt': '查看系统认证方式',
        'oauth/callback': 'oauth回调接口',
        'update_authn': '更新系统认证方式',
        'upload_transfer_file': '上传分发文件',
        'delete_transfer_file': '删除分发文件',

    }
    @wraps(func)
    def wrapper(request):
        user = request.user if request.user.is_authenticated else None
        action = URL_DESCRIPTIONS.get(request.resolver_match.url_name, "unknown page")
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            user_ip = x_forwarded_for.split(',')[0]
        else:
            user_ip = request.META.get('REMOTE_ADDR')

        general_audit.objects.create(user=user, action=action, extra_content=user_ip)

        return func(request)

    return wrapper