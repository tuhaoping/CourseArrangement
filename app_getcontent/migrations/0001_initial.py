# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-04-11 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='姓名', max_length=10)),
                ('title_teacher', models.CharField(db_column='教師職稱', max_length=10)),
                ('title_peoffice', models.CharField(blank=True, db_column='行政職稱', max_length=10, null=True)),
            ],
            options={
                'db_table': '列表_教師列表',
                'managed': False,
            },
        ),
    ]
