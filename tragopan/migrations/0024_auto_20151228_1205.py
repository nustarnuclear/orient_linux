# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0023_auto_20151130_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='material_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Compound or elementary substance'), (2, 'mixture')]),
        ),
        migrations.AlterField(
            model_name='controlrodassembly',
            name='type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'black rod'), (2, 'grey rod')]),
        ),
    ]
