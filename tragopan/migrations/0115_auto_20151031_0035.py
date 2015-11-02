# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0114_auto_20151031_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodassemblystep',
            name='step',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], max_digits=10),
        ),
    ]
