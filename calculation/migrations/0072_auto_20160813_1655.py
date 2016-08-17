# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0071_auto_20160511_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='bp',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_point',
            field=models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100', decimal_places=4, default=66),
        ),
    ]
