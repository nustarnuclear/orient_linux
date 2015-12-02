# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0022_auto_20151130_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationmonthlyparameter',
            name='FQ',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=10, help_text='unit:', blank=True),
        ),
        migrations.AlterField(
            model_name='operationmonthlyparameter',
            name='avg_burnup',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=15, help_text='unit:MWd/tU', blank=True),
        ),
        migrations.AlterField(
            model_name='operationmonthlyparameter',
            name='boron_concentration',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=10, help_text='unit:ppm', blank=True),
        ),
        migrations.AlterField(
            model_name='operationmonthlyparameter',
            name='relative_power',
            field=models.DecimalField(max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], null=True, decimal_places=9, blank=True),
        ),
    ]
