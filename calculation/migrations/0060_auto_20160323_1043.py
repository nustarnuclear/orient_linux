# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0059_auto_20160322_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobintask',
            name='server',
        ),
        migrations.AddField(
            model_name='robintask',
            name='server',
            field=models.ForeignKey(related_name='robin_tasks', to='calculation.Server', default=calculation.models.server_default),
        ),
    ]
