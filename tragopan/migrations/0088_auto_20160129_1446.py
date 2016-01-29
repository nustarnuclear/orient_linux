# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0087_auto_20160129_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelelementpelletloadingscheme',
            name='length',
            field=models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], decimal_places=3),
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='ave_mass_power_density',
            field=models.DecimalField(default=30, max_digits=15, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, help_text='unit:W/g (fuel)'),
            preserve_default=False,
        ),
    ]
