# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0027_auto_20151229_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='bpr_B10',
            field=models.DecimalField(help_text='mg/cm', validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=9, decimal_places=6, blank=True),
        ),
        migrations.AddField(
            model_name='material',
            name='enrichment',
            field=models.DecimalField(help_text='U235:%', validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=9, decimal_places=6, blank=True),
        ),
        migrations.AddField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 'fuel by enrichment'), (2, 'by B10 linear density'), (3, 'blend basic materials')], blank=True),
        ),
    ]
