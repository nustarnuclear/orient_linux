# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0018_auto_20151113_1648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassemblystep',
            name='control_rod_cluster',
        ),
        migrations.RemoveField(
            model_name='controlrodassemblystep',
            name='operation',
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='control_rod_step',
        ),
        migrations.DeleteModel(
            name='ControlRodAssemblyStep',
        ),
        migrations.DeleteModel(
            name='OperationParameter',
        ),
    ]
