# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0004_remove_egrettask_follow_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='task_visualbility',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, 'private'), (2, 'share to group'), (3, 'share to all')]),
        ),
    ]
