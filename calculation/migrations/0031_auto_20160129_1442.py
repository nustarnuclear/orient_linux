# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0030_auto_20160129_1414'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='last_modified',
        ),
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='remark',
        ),
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='time_inserted',
        ),
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='user',
        ),
    ]
