# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0111_controlrodassembly_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operationparameter',
            old_name='measured_boron_density',
            new_name='critical_boron_density',
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='coolant_average_temperature',
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='nuclear_power',
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='theoretical_boron_density',
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='unit',
        ),
        migrations.AddField(
            model_name='operationparameter',
            name='cycle',
            field=models.ForeignKey(default=1, to='tragopan.Cycle'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='operationparameter',
            name='relative_power',
            field=models.DecimalField(default=0.1, decimal_places=9, max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='operationparameter',
            name='axial_power_shift',
            field=models.DecimalField(max_digits=9, blank=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(-100)], help_text='unit:%FP', decimal_places=6, null=True),
        ),
    ]
