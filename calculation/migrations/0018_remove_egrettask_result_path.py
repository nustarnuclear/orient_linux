# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0017_auto_20151207_1429'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='result_path',
        ),
    ]
