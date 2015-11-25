# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0014_egrettask_calculation_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipleloadingpattern',
            name='authorized',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='task_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished')], default=0),
        ),
    ]
