# Generated by Django 5.1.3 on 2024-12-13 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salt', '0044_host_group_minion_minion_name_alter_hosts_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shell_template',
            name='content',
        ),
        migrations.AddField(
            model_name='shell_template',
            name='main',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='hosts',
            name='status',
            field=models.IntegerField(choices=[(3, 'pending'), (2, 'unknown'), (0, 'up'), (1, 'down'), (4, 'denied'), (5, 'rejected')]),
        ),
        migrations.AlterField(
            model_name='shell_template',
            name='description',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='shell_template',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='task_list',
            name='status',
            field=models.IntegerField(choices=[(2, '已完成'), (0, '待审批'), (3, '执行中'), (1, '待执行')], default=0),
        ),
    ]
