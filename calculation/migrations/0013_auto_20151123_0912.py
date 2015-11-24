# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0012_auto_20151113_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='egrettask',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
