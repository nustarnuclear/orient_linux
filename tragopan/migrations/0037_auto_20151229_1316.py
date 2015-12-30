# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0036_auto_20151229_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mixturecomposition',
            name='mixture',
            field=models.ForeignKey(related_name='mixtures', to='tragopan.Material'),
        ),
        migrations.AlterField(
            model_name='mixturecomposition',
            name='percent',
            field=models.DecimalField(default=0.5, max_digits=9, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], decimal_places=6, help_text='unit:%'),
        ),
    ]
