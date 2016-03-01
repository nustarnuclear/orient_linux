# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0040_auto_20160226_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='robintask',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='robintask',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
