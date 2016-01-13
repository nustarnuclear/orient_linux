# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0023_auto_20160113_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobinbranch',
            name='max_burnup_point',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, default=60, decimal_places=4, help_text='GWd/tU'),
        ),
    ]
