# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0061_auto_20160114_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblymodel',
            name='side_pin_num',
            field=models.PositiveSmallIntegerField(default=17),
        ),
    ]
