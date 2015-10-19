# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0026_auto_20151017_0157'),
    ]

    operations = [
        migrations.AddField(
            model_name='basefuel',
            name='offset',
            field=models.BooleanField(default=False),
        ),
    ]
