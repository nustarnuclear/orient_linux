# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0091_auto_20160202_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassemblytype',
            name='side_pin_num',
            field=models.PositiveSmallIntegerField(default=17),
        ),
        migrations.AlterField(
            model_name='controlrodassemblymap',
            name='control_rod_assembly_type',
            field=models.ForeignKey(to='tragopan.ControlRodAssemblyType', related_name='rod_positions'),
        ),
    ]
