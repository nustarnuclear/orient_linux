# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0009_egrettask_authorized'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basefuel',
            name='fuel_identity',
            field=models.CharField(unique=True, max_length=32),
        ),
    ]
