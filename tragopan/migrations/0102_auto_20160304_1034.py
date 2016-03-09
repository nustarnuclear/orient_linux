# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0101_remove_burnablepoisonrod_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelassemblymodel',
            name='overall_length',
        ),
        migrations.AddField(
            model_name='fuelassemblymodel',
            name='active_length',
            field=models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], default=365.8, max_digits=10, decimal_places=5),
        ),
    ]
