# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0154_auto_20160520_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblytype',
            name='Gd_num',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
