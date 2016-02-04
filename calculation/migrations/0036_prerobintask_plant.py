# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0088_auto_20160129_1446'),
        ('calculation', '0035_prerobintask_fuel_assembly_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='plant',
            field=models.ForeignKey(to='tragopan.Plant', default=2),
            preserve_default=False,
        ),
    ]
