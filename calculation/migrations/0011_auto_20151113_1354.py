# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0010_auto_20151112_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basefuel',
            name='fuel_identity',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
#(default=calculation.models.fuel_identity_default,