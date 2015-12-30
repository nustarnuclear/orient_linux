# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0037_auto_20151229_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mixturecomposition',
            name='percent',
            field=models.DecimalField(max_digits=9, help_text='unit:%', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], decimal_places=6),
        ),
    ]
