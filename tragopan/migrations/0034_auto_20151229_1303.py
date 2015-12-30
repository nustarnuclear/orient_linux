# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0033_auto_20151229_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='mixturecomposition',
            name='volume_percent',
            field=models.DecimalField(help_text='unit:%', blank=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='mixturecomposition',
            name='weight_percent',
            field=models.DecimalField(help_text='unit:%', blank=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], decimal_places=6, max_digits=9, null=True),
        ),
    ]
