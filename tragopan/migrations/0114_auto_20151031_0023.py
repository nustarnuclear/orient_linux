# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0113_auto_20151030_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationparameter',
            name='critical_boron_density',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, max_digits=10, help_text='unit:ppm'),
        ),
    ]
