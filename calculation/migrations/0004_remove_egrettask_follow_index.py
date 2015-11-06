# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0003_egrettask_pre_egret_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='follow_index',
        ),
    ]
