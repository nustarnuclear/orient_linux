# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0099_auto_20160301_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='sleeve_volume',
            field=models.DecimalField(max_digits=10, decimal_places=5, help_text='cm3', validators=[django.core.validators.MinValueValidator(0)], default=741),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grid',
            name='spring_volume',
            field=models.DecimalField(max_digits=10, decimal_places=5, help_text='cm3', validators=[django.core.validators.MinValueValidator(0)], default=80),
            preserve_default=False,
        ),
    ]
