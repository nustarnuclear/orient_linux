# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0064_auto_20160125_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='fuel_assembly_model',
            field=models.ForeignKey(to='tragopan.FuelAssemblyModel', related_name='bp_rod'),
        ),
    ]
