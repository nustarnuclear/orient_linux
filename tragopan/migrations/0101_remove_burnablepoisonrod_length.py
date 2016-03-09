# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0100_auto_20160301_1610'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonrod',
            name='length',
        ),
    ]
