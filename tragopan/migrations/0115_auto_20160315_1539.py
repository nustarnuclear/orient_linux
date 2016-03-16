# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0114_auto_20160315_1538'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='burnablepoisonassembly',
            order_with_respect_to='fuel_assembly_model',
        ),
    ]
