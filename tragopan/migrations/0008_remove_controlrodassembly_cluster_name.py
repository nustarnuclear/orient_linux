# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0007_controlrodassembly_cluster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='cluster_name',
        ),
    ]
