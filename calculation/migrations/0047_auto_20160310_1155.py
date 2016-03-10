# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0046_auto_20160310_0927'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='robintask',
            name='log_file',
        ),
        migrations.RemoveField(
            model_name='robintask',
            name='output_file',
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='server',
            field=models.ForeignKey(related_name='pre_robin_tasks', to='calculation.Server', default=calculation.models.server_default),
        ),
    ]
