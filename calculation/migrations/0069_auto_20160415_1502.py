# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0068_auto_20160414_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corebafflecalculation',
            name='fuel_assembly_type',
        ),
        migrations.AddField(
            model_name='corebafflecalculation',
            name='pre_robin_task',
            field=models.ForeignKey(default=240, to='calculation.PreRobinTask'),
            preserve_default=False,
        ),
    ]
