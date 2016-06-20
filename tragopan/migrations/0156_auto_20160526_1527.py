# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0155_fuelassemblytype_gd_num'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operationdailyparameter',
            options={'verbose_name_plural': 'Daily operation history', 'verbose_name': 'Daily operation history'},
        ),
        migrations.AlterModelOptions(
            name='operationmonthlyparameter',
            options={'verbose_name': 'Incore flux mapping result'},
        ),
        migrations.AlterField(
            model_name='fuelassemblymodel',
            name='lower_gap',
            field=models.DecimalField(decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fuelassemblymodel',
            name='side_length',
            field=models.DecimalField(decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fuelassemblymodel',
            name='upper_gap',
            field=models.DecimalField(decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fuelassemblymodel',
            name='vendor',
            field=models.ForeignKey(to='tragopan.Vendor', null=True, blank=True),
        ),
    ]
