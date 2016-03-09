# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0042_auto_20160307_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('IP', models.GenericIPAddressField()),
                ('status', models.CharField(default='B', max_length=1, choices=[('A', 'available'), ('B', 'busy')])),
            ],
            options={
                'db_table': 'server',
            },
        ),
    ]
