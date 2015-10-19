# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0101_auto_20151012_2347'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='material',
            table='material',
        ),
        migrations.AlterModelTable(
            name='nuclide',
            table='nuclide',
        ),
    ]
