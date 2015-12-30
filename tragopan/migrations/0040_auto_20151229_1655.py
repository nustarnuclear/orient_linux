# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0039_auto_20151229_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='operationdailyparameter',
            name='delta_time',
            field=models.DecimalField(max_digits=15, validators=[django.core.validators.MinValueValidator(0)], null=True, decimal_places=5, help_text='unit:day', blank=True),
        ),
        migrations.AlterField(
            model_name='controlrodassemblystep',
            name='operation',
            field=models.ForeignKey(related_name='control_rods', to='tragopan.OperationDailyParameter'),
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'fuel by enrichment'), (2, 'blend materials with B10 linear density'), (3, 'blend materials '), (4, 'totally inherit from basic material'), (5, 'inherit from basic material with B10 linear density')], default=1),
        ),
        migrations.AlterField(
            model_name='operationdailyparameter',
            name='burnup',
            field=models.DecimalField(max_digits=15, validators=[django.core.validators.MinValueValidator(0)], null=True, decimal_places=5, help_text='unit:MWd/tU', blank=True),
        ),
    ]
