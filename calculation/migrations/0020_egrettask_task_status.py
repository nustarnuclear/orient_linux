# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0019_auto_20150928_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='task_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'not yet'), (1, 'finished')], default=0),
        ),
    ]
