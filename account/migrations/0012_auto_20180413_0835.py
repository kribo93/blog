# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-13 08:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20180413_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='nickname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
