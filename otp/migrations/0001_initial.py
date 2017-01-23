# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 15:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_auth', models.DateTimeField(null=True)),
                ('last_2fa', models.DateTimeField(null=True)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sessions.Session')),
            ],
        ),
    ]