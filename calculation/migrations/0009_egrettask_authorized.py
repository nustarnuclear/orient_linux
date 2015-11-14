# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0008_remove_ibis_ibis_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='authorized',
            field=models.BooleanField(default=False),
        ),
    ]
