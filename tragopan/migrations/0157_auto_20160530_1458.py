# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0156_auto_20160526_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelassemblyrepository',
            name='vendor',
            field=models.ForeignKey(blank=True, to='tragopan.Vendor', null=True),
        ),
    ]
