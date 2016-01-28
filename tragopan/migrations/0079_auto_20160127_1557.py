# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0078_auto_20160127_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelelement',
            name='radial_map',
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='radius',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, help_text='unit:cm', max_digits=7, default=0.4095),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fuelelement',
            name='active_length',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=3, help_text='unit:cm', max_digits=7, default=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fuelelement',
            name='overall_length',
            field=models.DecimalField(help_text='unit:cm', decimal_places=3, validators=[django.core.validators.MinValueValidator(0)], blank=True, max_digits=7, null=True),
        ),
    ]
