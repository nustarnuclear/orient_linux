# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0115_auto_20151031_0035'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitparameter',
            name='best_estimated_cool_mass_flow_rate',
            field=models.DecimalField(null=True, help_text='unit:kg/h', blank=True, max_digits=15, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='unitparameter',
            name='coolant_volume',
            field=models.DecimalField(null=True, help_text='unit:m3', blank=True, max_digits=20, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
