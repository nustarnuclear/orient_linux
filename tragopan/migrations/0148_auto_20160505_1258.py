# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0147_grid_spring_material'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grid',
            name='sleeve_material',
            field=models.ForeignKey(to='tragopan.Material', related_query_name='grid_sleeve', null=True, related_name='grid_sleeves'),
        ),
        migrations.AlterField(
            model_name='grid',
            name='spring_volume',
            field=models.DecimalField(max_digits=10, validators=[django.core.validators.MinValueValidator(0)], null=True, blank=True, help_text='cm3', decimal_places=5),
        ),
    ]
