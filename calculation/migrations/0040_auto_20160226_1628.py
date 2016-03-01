# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0039_robintask'),
    ]

    operations = [
        migrations.RenameField(
            model_name='robintask',
            old_name='pre_robin_model',
            new_name='pre_robin_task',
        ),
    ]
