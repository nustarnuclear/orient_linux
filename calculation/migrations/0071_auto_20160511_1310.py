# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0070_auto_20160425_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robintask',
            name='server',
            field=models.ForeignKey(blank=True, related_name='robin_tasks', null=True, to='calculation.Server'),
        ),
    ]
