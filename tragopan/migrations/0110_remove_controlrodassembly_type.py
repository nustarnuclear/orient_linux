# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0109_auto_20151020_2305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='type',
        ),
    ]
