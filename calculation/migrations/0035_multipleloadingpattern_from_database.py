# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0034_auto_20151023_0035'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipleloadingpattern',
            name='from_database',
            field=models.BooleanField(default=False),
        ),
    ]
