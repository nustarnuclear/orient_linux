# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0066_auto_20160125_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonassembly',
            name='burnable_poison_map',
        ),
        migrations.AlterField(
            model_name='burnablepoisonassemblymap',
            name='burnable_poison_assembly',
            field=models.ForeignKey(to='tragopan.BurnablePoisonAssembly', related_name='rod_positions'),
        ),
        migrations.AlterField(
            model_name='burnablepoisonrodmap',
            name='burnable_poison_assembly',
            field=models.ForeignKey(to='tragopan.BurnablePoisonAssembly'),
        ),
        migrations.AlterField(
            model_name='fuelassemblyposition',
            name='fuel_assembly_model',
            field=models.ForeignKey(to='tragopan.FuelAssemblyModel', related_name='positions'),
        ),
    ]
