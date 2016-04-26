# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0137_auto_20160413_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corebaffle',
            name='outer_diameter',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], null=True, max_digits=7, decimal_places=3, help_text='unit:cm', blank=True),
        ),
        migrations.AlterField(
            model_name='corebaffle',
            name='thickness',
            field=models.DecimalField(default=2.875, decimal_places=3, max_digits=7, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]
