# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-04-11 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_getcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaceList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_num', models.CharField(max_length=2, verbose_name='場地代號')),
                ('second_num', models.CharField(max_length=5, verbose_name='場地編號')),
                ('place', models.CharField(max_length=10, verbose_name='場地名稱')),
                ('note', models.CharField(blank=True, max_length=50, null=True, verbose_name='備註')),
            ],
            options={
                'db_table': '列表_場地列表',
                'managed': False,
            },
        ),
    ]
