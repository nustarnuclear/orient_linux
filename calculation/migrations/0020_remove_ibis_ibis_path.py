# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0019_auto_20151215_1053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ibis',
            name='ibis_path',
        ),
    ]
