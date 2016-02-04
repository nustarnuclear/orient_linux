# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0088_auto_20160129_1446'),
        ('calculation', '0034_auto_20160201_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='fuel_assembly_type',
            field=models.ForeignKey(default=2, to='tragopan.FuelAssemblyType'),
            preserve_default=False,
        ),
    ]
