# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0057_auto_20160321_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='bp_in',
            field=models.BooleanField(default=False),
        ),
    ]
