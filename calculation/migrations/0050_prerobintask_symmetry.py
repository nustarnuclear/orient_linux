# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0049_remove_robintask_pid'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='symmetry',
            field=models.BooleanField(default=True),
        ),
    ]
