# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0074_prerobintask_pellet_map'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobininput',
            name='burnup_point',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100', default=32, decimal_places=4),
        ),
    ]
