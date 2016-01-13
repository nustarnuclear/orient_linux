# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0041_auto_20160111_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelelement',
            name='fuel_assembly_model',
            field=models.ForeignKey(to='tragopan.FuelAssemblyModel', related_name='fuel_elements'),
        ),
    ]
