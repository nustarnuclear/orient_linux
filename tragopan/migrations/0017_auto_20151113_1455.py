# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0016_auto_20151112_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelassemblyrepository',
            name='PN',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
