# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-27 11:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coredata', '0016_create_enrolmenthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='expiry',
            field=models.DateField(default=datetime.date(2018, 4, 1)),
            preserve_default=False,
        ),
    ]
