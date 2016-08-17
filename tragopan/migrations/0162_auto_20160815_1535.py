# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0161_auto_20160815_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelelementsection',
            name='length',
            field=models.DecimalField(max_digits=10, decimal_places=5, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
