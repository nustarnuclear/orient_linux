# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0153_auto_20160520_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblyrepository',
            name='broken_cycle',
            field=models.ForeignKey(to='tragopan.Cycle', null=True, blank=True, related_name='broken_assemblies'),
        ),
        migrations.AddField(
            model_name='fuelassemblyrepository',
            name='unavailable_cycle',
            field=models.ForeignKey(to='tragopan.Cycle', null=True, blank=True, related_name='unavailable_assemblies'),
        ),
    ]
