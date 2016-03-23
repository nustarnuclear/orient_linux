# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0123_auto_20160318_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblyloadingpattern',
            name='burnable_poison_assembly',
            field=models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True, related_name='bpa'),
        ),
        migrations.AddField(
            model_name='fuelassemblyloadingpattern',
            name='control_rod_assembly',
            field=models.ForeignKey(to='tragopan.ControlRodAssembly', null=True, blank=True, related_name='cra'),
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Compound or elementary substance'), (2, 'mixture')], default=1),
        ),
    ]
