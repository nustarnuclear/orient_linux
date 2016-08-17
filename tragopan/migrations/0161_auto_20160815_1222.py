# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0160_auto_20160815_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelpellet',
            name='fuel_assembly_model',
            field=models.ForeignKey(to='tragopan.FuelAssemblyModel'),
        ),
    ]
