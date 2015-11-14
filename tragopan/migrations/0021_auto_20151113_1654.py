# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0020_auto_20151113_1651'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='operationdailyparameter',
            table='operation_daily_parameter',
        ),
    ]
