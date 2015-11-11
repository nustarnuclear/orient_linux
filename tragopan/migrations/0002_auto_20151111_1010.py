# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblyrepository',
            name='broken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fuelassemblyrepository',
            name='unit',
            field=models.ForeignKey(null=True, related_name='fuel_assemblies', blank=True, to='tragopan.UnitParameter'),
        ),
    ]
