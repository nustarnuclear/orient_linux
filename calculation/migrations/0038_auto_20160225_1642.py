# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0037_auto_20160224_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='task_status',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'cancled'), (6, 'errored')]),
        ),
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_unit',
            field=models.CharField(default='"GWd/tU"', choices=[('GWd/tU', 'GWd/tU'), ('DGWd/tU"', 'DGWd/tU'), ('day', 'day'), ('Dday', 'Dday')], max_length=9),
        ),
    ]
