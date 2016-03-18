# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0122_auto_20160318_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='density',
        ),
        migrations.AddField(
            model_name='material',
            name='density_percent',
            field=models.DecimalField(max_digits=9, default=100, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], help_text='unit:%', decimal_places=6),
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'fuel by enrichment'), (2, 'blend basic materials by weight percent and B10 linear density'), (3, 'symbolic'), (6, 'blend basic materials by weight percent and density')], default=1),
        ),
    ]
