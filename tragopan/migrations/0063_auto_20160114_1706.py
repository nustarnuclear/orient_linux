# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0062_fuelassemblymodel_side_pin_num'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fuelassemblytype',
            old_name='fuel_element_type_position',
            new_name='map',
        ),
        migrations.AlterField(
            model_name='grid',
            name='fuel_assembly_model',
            field=models.ForeignKey(related_name='grids', to='tragopan.FuelAssemblyModel'),
        ),
        migrations.AlterField(
            model_name='gridposition',
            name='fuel_assembly_model',
            field=models.ForeignKey(related_name='grid_pos', to='tragopan.FuelAssemblyModel'),
        ),
    ]
