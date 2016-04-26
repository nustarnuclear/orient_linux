# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0067_remove_corebafflecalculation_depletion_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='min_avail_subtask_num',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='recalculation_depth',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
