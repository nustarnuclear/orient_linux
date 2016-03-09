# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0098_auto_20160224_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodtype',
            name='radius',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=5, help_text='unit:cm', default=0.48385),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'fuel by enrichment'), (2, 'blend basic materials by weight percent and B10 linear density'), (3, 'blend materials by volume percent'), (6, 'blend basic materials by weight percent and density')]),
        ),
    ]
