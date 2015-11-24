# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0013_auto_20151123_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='calculation_identity',
            field=models.CharField(max_length=128, blank=True),
        ),
    ]
