# Generated by Django 5.1.3 on 2025-01-07 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salt', '0068_alter_authenticate_type_type_alter_hosts_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authenticate_type',
            name='type',
            field=models.IntegerField(choices=[(2, 'OAuth'), (0, 'Internal'), (1, 'LDAP')], default=0),
        ),
        migrations.AlterField(
            model_name='hosts',
            name='status',
            field=models.IntegerField(choices=[(5, 'rejected'), (0, 'up'), (1, 'down'), (4, 'denied'), (2, 'unknown'), (3, 'pending')]),
        ),
        migrations.AlterField(
            model_name='task_list',
            name='status',
            field=models.IntegerField(choices=[(1, '待执行'), (2, '已完成'), (3, '执行中'), (0, '待审批')], default=0),
        ),
        migrations.AlterField(
            model_name='transfer_file',
            name='name',
            field=models.CharField(default='', max_length=300, unique=True),
        ),
    ]
