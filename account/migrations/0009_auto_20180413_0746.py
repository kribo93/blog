# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-13 07:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20180413_0737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.CharField(max_length=50),
        ),
    ]
