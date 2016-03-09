# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0103_auto_20160304_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialweightcomposition',
            name='percent',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], help_text='unit:%', max_digits=8),
        ),
        migrations.AlterField(
            model_name='mixturecomposition',
            name='percent',
            field=models.DecimalField(decimal_places=5, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], help_text='unit:%', max_digits=8),
        ),
    ]
