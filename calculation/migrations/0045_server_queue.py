# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0044_auto_20160309_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='queue',
            field=models.CharField(max_length=32, unique=True, default='queue0'),
            preserve_default=False,
        ),
    ]
