# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0016_egrettask_recalculation_depth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='egrettask',
            name='loading_pattern',
            field=models.ForeignKey(blank=True, to='calculation.MultipleLoadingPattern', null=True),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='task_status',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'cancled'), (6, 'errored')]),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='task_type',
            field=models.CharField(choices=[('FOLLOW', 'follow'), ('SEQUENCE', 'auto sequence')], max_length=32),
        ),
    ]
