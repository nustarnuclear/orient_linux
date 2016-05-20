# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0150_auto_20160518_1029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operationdistributiondata',
            old_name='axial_power_shift',
            new_name='axial_power_offset',
        ),
        migrations.AlterField(
            model_name='operationbankposition',
            name='operation',
            field=models.ForeignKey(to='tragopan.OperationMonthlyParameter', related_name='cluster_steps'),
        ),
        migrations.AlterField(
            model_name='operationdistributiondata',
            name='operation',
            field=models.ForeignKey(to='tragopan.OperationMonthlyParameter', related_name='distribution_data'),
        ),
    ]
