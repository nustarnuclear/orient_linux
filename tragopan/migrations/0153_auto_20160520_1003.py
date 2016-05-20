# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0152_auto_20160520_1001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operationmonthlyparameter',
            old_name='axial_power_shift',
            new_name='axial_power_offset',
        ),
    ]
