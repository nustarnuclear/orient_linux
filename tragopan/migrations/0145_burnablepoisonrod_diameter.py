# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0144_auto_20160421_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='burnablepoisonrod',
            name='diameter',
            field=models.DecimalField(max_digits=7, default=0.4838, help_text='unit:cm', decimal_places=3, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
