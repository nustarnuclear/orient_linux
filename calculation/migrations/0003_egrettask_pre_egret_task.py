# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0002_remove_egrettask_restart_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='pre_egret_task',
            field=models.ForeignKey(to='calculation.EgretTask', related_name='post_egret_tasks', blank=True, null=True),
        ),
    ]
