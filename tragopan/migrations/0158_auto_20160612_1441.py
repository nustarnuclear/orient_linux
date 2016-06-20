# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0157_auto_20160530_1458'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='controlrodassemblytype',
            options={'verbose_name': 'Control rod assembly'},
        ),
        migrations.AlterModelOptions(
            name='controlrodtype',
            options={'verbose_name': 'Control rod'},
        ),
        migrations.RemoveField(
            model_name='fuelassemblyloadingpattern',
            name='rotation_degree',
        ),
        migrations.AlterField(
            model_name='fuelassemblyrepository',
            name='unit',
            field=models.ForeignKey(to='tragopan.UnitParameter', null=True, related_name='fuel_assemblies'),
        ),
        migrations.AlterField(
            model_name='reactormodel',
            name='fuel_pitch',
            field=models.DecimalField(max_digits=7, help_text='unit:cm', decimal_places=3, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AlterField(
            model_name='reactormodel',
            name='vendor',
            field=models.ForeignKey(blank=True, to='tragopan.Vendor', null=True),
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='best_estimated_cool_mass_flow_rate',
            field=models.DecimalField(max_digits=15, help_text='unit:kg/h', decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='coolant_volume',
            field=models.DecimalField(max_digits=20, help_text='unit:m3', decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
    ]
