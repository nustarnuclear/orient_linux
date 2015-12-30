# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0038_auto_20151229_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'fuel by enrichment'), (2, 'blend basic materials with B10 linear density'), (3, 'blend basic materials '), (4, 'totally inherit from basic material'), (5, 'inherit from basic material with B10 linear density')]),
        ),
        migrations.AlterModelTable(
            name='basicelementcomposition',
            table='basic_element_composition',
        ),
    ]
