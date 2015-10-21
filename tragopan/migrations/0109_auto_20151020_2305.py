# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0108_auto_20151020_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodassembly',
            name='basez',
            field=models.DecimalField(max_digits=7, decimal_places=5, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='controlrodassembly',
            name='step_size',
            field=models.DecimalField(max_digits=7, decimal_places=5, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
