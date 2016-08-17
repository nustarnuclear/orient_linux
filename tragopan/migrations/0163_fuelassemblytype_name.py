# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0162_auto_20160815_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblytype',
            name='name',
            field=models.CharField(max_length=10, default=''),
            preserve_default=False,
        ),
    ]
