# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0029_auto_20160129_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_point',
            field=models.DecimalField(decimal_places=4, help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, default=60),
        ),
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_unit',
            field=models.CharField(max_length=7, choices=[('GWd/tU', 'GWd/tU'), ('DGWd/tU', 'DGWd/tU'), ('day', 'day'), ('Dday', 'Dday')], default='GWd/tU'),
        ),
    ]
