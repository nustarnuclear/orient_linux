# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0056_auto_20160317_0935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='shutdown_cooling_days',
        ),
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='xenon',
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='max_burnup_point',
            field=models.DecimalField(decimal_places=4, validators=[django.core.validators.MinValueValidator(0)], default=65, help_text='GWd/tU', max_digits=7),
        ),
    ]
