# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0085_auto_20160128_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelelementtypeposition',
            name='fuel_assembly_type',
            field=models.ForeignKey(to='tragopan.FuelAssemblyType', related_name='rod_positions'),
        ),
    ]
