# Generated by Django 5.1.3 on 2024-11-07 09:44

import mirage.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='salt_master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=300)),
                ('host', models.CharField(max_length=200, verbose_name='Salt Master')),
                ('user', mirage.fields.EncryptedCharField(blank=True, default='', max_length=200)),
                ('password', mirage.fields.EncryptedCharField(blank=True, default='', max_length=300)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
        ),
    ]
