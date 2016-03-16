# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0111_auto_20160309_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gridposition',
            name='fuel_assembly_model',
            field=models.ForeignKey(related_name='grid_positions', to='tragopan.FuelAssemblyModel'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='controlrodassemblytype',
            order_with_respect_to='reactor_model',
        ),
    ]
