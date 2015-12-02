# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0015_auto_20151125_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='recalculation_depth',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
