# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0121_remove_unitparameter_reactor_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelpellet',
            name='dish_depth',
        ),
        migrations.RemoveField(
            model_name='fuelpellet',
            name='dish_diameter',
        ),
        migrations.RemoveField(
            model_name='fuelpellet',
            name='nominal_density',
        ),
        migrations.RemoveField(
            model_name='fuelpellet',
            name='roughness',
        ),
        migrations.RemoveField(
            model_name='fuelpellet',
            name='uncertainty_percentage',
        ),
        migrations.AddField(
            model_name='fuelpellet',
            name='nominal_density_percent',
            field=models.DecimalField(help_text='unit:%', max_digits=9, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], decimal_places=6, default=95),
        ),
    ]
