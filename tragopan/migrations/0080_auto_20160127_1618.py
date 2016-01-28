# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0079_auto_20160127_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelelementradialmap',
            name='fuel_element',
        ),
        migrations.RemoveField(
            model_name='fuelelementradialmap',
            name='material',
        ),
        migrations.AlterField(
            model_name='fuelelement',
            name='filling_gas_material',
            field=models.ForeignKey(related_name='filling_fuel_elements', default=46, to='tragopan.Material'),
        ),
        migrations.DeleteModel(
            name='FuelElementRadialMap',
        ),
    ]
