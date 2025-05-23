# Generated by Django 5.1.3 on 2025-04-29 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salt', '0083_alter_authenticate_type_type_alter_host_group_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shell_template',
            name='extra_vars',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='shell_template',
            name='main_dir',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='authenticate_type',
            name='type',
            field=models.IntegerField(choices=[(2, 'OAuth'), (0, 'Internal'), (1, 'LDAP')], default=0),
        ),
        migrations.AlterField(
            model_name='hosts',
            name='status',
            field=models.IntegerField(choices=[(2, 'unknown'), (0, 'up'), (3, 'pending'), (5, 'rejected'), (4, 'denied'), (1, 'down')]),
        ),
        migrations.AlterField(
            model_name='shell_template',
            name='type',
            field=models.IntegerField(choices=[(0, 'state'), (1, 'shell'), (2, 'playbook')], default=1),
        ),
        migrations.AlterField(
            model_name='task_list',
            name='status',
            field=models.IntegerField(choices=[(1, '待执行'), (3, '执行中'), (6, '被终止'), (5, '已撤回'), (4, '被拒绝'), (2, '已完成'), (0, '待审批')], default=0),
        ),
    ]
