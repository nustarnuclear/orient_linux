# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0102_auto_20151017_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grid',
            name='inner_sleeve_thickness',
            field=models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=5, help_text='cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='grid',
            name='outer_sleeve_thickness',
            field=models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=5, help_text='cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='grid',
            name='side_length',
            field=models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=5, help_text='cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
