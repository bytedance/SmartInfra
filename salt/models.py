from tempfile import template

from django.db import models
from mirage import fields
from django.contrib.auth.models import User
# Create your models here.

master_type_choices = {
    (0, "saltstack"),
    (1, "ansible"),

}

class salt_master(models.Model):
    """
    SaltMaster配置
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    type = models.IntegerField(choices=master_type_choices, default=0)
    host = models.CharField("Salt Master", max_length=200)
    user = fields.EncryptedCharField(max_length=200, default="")
    password = fields.EncryptedTextField(default="")
    minion_name = models.CharField(max_length=300, default="")
    file_roots = models.CharField(max_length=300, default="")
    sftp_port = models.IntegerField(default=22)
    sftp_user = fields.EncryptedCharField(
        max_length=200, default="", blank=True
    )
    sftp_password = fields.EncryptedCharField(
        max_length=300, default="", blank=True
    )
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

template_type_choices = {
    (0, "state"),
    (1, "shell"),
    (2, "playbook"),

}

class shell_template(models.Model):
    """
    命令模板配置
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500)
    main_content = models.TextField(default="")
    func_content = models.TextField(default="")
    type = models.IntegerField(choices=template_type_choices, default=1)
    file_name = models.CharField(max_length=100, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class resource_group(models.Model):
    """
    资源组管理
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class acl_manage(models.Model):
    """
    acl策略管理
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    content = models.CharField(max_length=600)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class rg_relationship(models.Model):
    """
    资源组和Salt, acl相关
    """
    rg = models.ForeignKey(resource_group, on_delete=models.CASCADE, null=True, default="")
    salt = models.ForeignKey(salt_master, on_delete=models.CASCADE, null=True, default="")
    acl = models.ForeignKey(acl_manage, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class user_relationship(models.Model):
    """
    用户相关的所有权限控制
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    rg = models.ForeignKey(resource_group, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class hosts(models.Model):
    """
    受管主机管理
    """
    host_status_choices = {
        (0, "up"),
        (1, "down"),
        (2, "unknown"),
        (3, "pending"),
        (4, "denied"),
        (5, "rejected"),

    }
    name = models.CharField(max_length=300)
    salt = models.ForeignKey(salt_master, on_delete=models.CASCADE, null=True, default="")
    status = models.IntegerField(choices=host_status_choices)
    label = models.IntegerField(default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class host_group(models.Model):
    """
    主机分组管理
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    host_num = models.IntegerField(default=0)
    type = models.IntegerField(choices=master_type_choices, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class host_group_minion(models.Model):
    """
    主机分组内主机详细信息
    """
    host_group_name = models.ForeignKey(host_group, on_delete=models.CASCADE, null=True, default="")
    minion_name = models.CharField(max_length=300, default="")
    salt_name = models.ForeignKey(salt_master, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

task_status_choices = {
    (0, "待审批"),
    (1, "待执行"),
    (2, "已完成"),
    (3, "执行中"),
    (4, "被拒绝"),
    (5, "已撤回"),

}

class task_list(models.Model):
    """
    执行的任务列表
    """
    name = models.CharField(max_length=500, default="")
    execute_content = models.TextField(default="")
    execute_policy = models.CharField(max_length=50, default="")
    host_group_name = models.ForeignKey(host_group, on_delete=models.CASCADE, null=True, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="", related_name="user_task_list")
    status = models.IntegerField(choices=task_status_choices, default=0)
    execute_result = models.CharField(max_length=600, default="")
    related_schedule = models.IntegerField(default=0)
    approve_result = models.TextField(default="")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="", related_name="approver_task_list")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class general_audit(models.Model):
    """
    用户登录登出审计
    """
    action = models.CharField(max_length=50, default="")
    extra_content = models.CharField(max_length=200, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

authenticate_type_choices = {
    (0, "Internal"),
    (1, "LDAP"),
    (2, "OAuth"),

}

class authenticate_type(models.Model):
    """
    用户认证方式
    """
    type = models.IntegerField(choices=authenticate_type_choices, default=0)
    name = models.CharField(max_length=50, default="authentication")
    client_id = models.CharField(max_length=100, default="")
    client_secret = models.CharField(max_length=200, default="")
    redirect_url = models.CharField(max_length=300, default="")
    authorization_url = models.CharField(max_length=300, default="")
    access_token_url = models.CharField(max_length=300, default="")
    resource_url = models.CharField(max_length=300, default="")
    grant_type = models.CharField(max_length=200, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

class transfer_file(models.Model):
    """
    上传分发文件管理
    """
    name = models.CharField(max_length=300, default="", unique=True)
    dest_dir = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    type = models.IntegerField(choices=master_type_choices, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)