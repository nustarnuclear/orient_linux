# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0060_auto_20160323_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assemblylamination',
            name='pre_robin_task',
            field=models.ForeignKey(to='calculation.PreRobinTask', related_name='layers'),
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='fuel_map',
            field=models.CommaSeparatedIntegerField(help_text='material pk', max_length=256),
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='pin_map',
            field=models.CommaSeparatedIntegerField(help_text='material transection pk', max_length=256),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
