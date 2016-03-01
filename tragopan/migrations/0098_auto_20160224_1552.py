# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0097_auto_20160224_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='basic_material',
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'fuel by enrichment'), (2, 'blend basic materials by B10 linear density'), (3, 'blend materials by volume percent'), (5, 'inherit from basic material with B10 linear density'), (6, 'blend basic materials by weight percent')]),
        ),
    ]
