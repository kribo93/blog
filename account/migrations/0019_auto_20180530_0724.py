# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-30 07:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_auto_20180530_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='taggit.Tag'),
        ),
    ]