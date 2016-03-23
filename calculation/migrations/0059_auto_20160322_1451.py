# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0058_prerobintask_bp_in'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobintask',
            name='bp_in',
        ),
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_point',
            field=models.DecimalField(help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100', validators=[django.core.validators.MinValueValidator(0)], decimal_places=4, default=65, max_digits=7),
        ),
    ]
