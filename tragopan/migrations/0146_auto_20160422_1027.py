# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0145_burnablepoisonrod_diameter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='diameter',
            field=models.DecimalField(max_digits=7, default=0.4838, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, help_text='unit:cm'),
        ),
    ]
