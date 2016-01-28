# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0077_auto_20160127_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelelement',
            name='coated',
            field=models.BooleanField(help_text='whether coated with some materials', default=False),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='coating_bottom',
            field=models.DecimalField(help_text='unit:cm based on the bottom of the active part', decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='coating_material',
            field=models.ForeignKey(null=True, blank=True, related_name='coating_fuel_elements', to='tragopan.Material'),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='coating_thickness',
            field=models.DecimalField(help_text='unit:cm', decimal_places=5, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='coating_top',
            field=models.DecimalField(help_text='unit:cm based on the bottom of the active part', decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='filling_gas_material',
            field=models.ForeignKey(null=True, blank=True, related_name='filling_fuel_elements', to='tragopan.Material'),
        ),
    ]
