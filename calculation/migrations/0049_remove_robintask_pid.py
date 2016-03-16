# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0048_robintask_pid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='robintask',
            name='pid',
        ),
    ]
