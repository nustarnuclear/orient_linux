# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0110_auto_20160307_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelpellet',
            name='chamfer_volume_percentage',
            field=models.DecimalField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], help_text='unit:%', default=0.1, decimal_places=6, max_digits=9),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fuelpellet',
            name='dish_volume_percentage',
            field=models.DecimalField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], help_text='unit:%', default=0.1, decimal_places=6, max_digits=9),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fuelpellet',
            name='length',
            field=models.DecimalField(blank=True, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, null=True, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='fuelpellet',
            name='outer_diameter',
            field=models.DecimalField(blank=True, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, null=True, decimal_places=5),
        ),
    ]
