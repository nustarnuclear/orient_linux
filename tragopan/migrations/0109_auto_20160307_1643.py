# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0108_grid_type_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='volume_composition',
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'fuel by enrichment'), (2, 'blend basic materials by weight percent and B10 linear density'), (6, 'blend basic materials by weight percent and density')], default=1),
        ),
    ]
