# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0063_auto_20160407_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multipleloadingpattern',
            name='from_database',
        ),
    ]
