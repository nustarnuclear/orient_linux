# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0055_remove_controlrodassembly_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodcluster',
            name='map',
        ),
    ]
