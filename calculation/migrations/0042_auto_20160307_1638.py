# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0041_auto_20160229_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_unit',
            field=models.CharField(max_length=9, choices=[('GWd/tU', 'GWd/tU'), ('DGWd/tU"', 'DGWd/tU'), ('day', 'day'), ('Dday', 'Dday')], default='GWd/tU'),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='task_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'canceled'), (6, 'error')], default=0),
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='task_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'canceled'), (6, 'error')], default=0),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='pre_robin_task',
            field=models.ForeignKey(related_name='robin_tasks', to='calculation.PreRobinTask'),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='task_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'canceled'), (6, 'error')], default=0),
        ),
        migrations.AlterUniqueTogether(
            name='prerobininput',
            unique_together=set([('unit', 'fuel_assembly_type', 'burnable_poison_assembly')]),
        ),
    ]
