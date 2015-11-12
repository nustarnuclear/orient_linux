# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0005_reactorposition_control_rod_cluster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reactorposition',
            name='control_rod_mechanism',
        ),
    ]
