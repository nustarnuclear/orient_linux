# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0036_prerobintask_plant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depletionstate',
            name='burnup_unit',
            field=models.CharField(default='"GWd/tU"', max_length=9, choices=[('"GWd/tU"', '"GWd/tU"'), ('"DGWd/tU"', '"DGWd/tU"'), ('day', 'day'), ('Dday', 'Dday')]),
        ),
    ]
