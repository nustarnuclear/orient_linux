# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0005_egrettask_task_visualbility'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='task_visualbility',
        ),
        migrations.AddField(
            model_name='egrettask',
            name='visibility',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, 'private'), (2, 'share to group'), (3, 'share to all')]),
        ),
        migrations.AddField(
            model_name='multipleloadingpattern',
            name='visibility',
            field=models.PositiveSmallIntegerField(default=3, choices=[(1, 'private'), (2, 'share to group'), (3, 'share to all')]),
        ),
    ]
