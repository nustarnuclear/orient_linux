# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0048_auto_20160113_0944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='control_rod_map',
        ),
    ]
