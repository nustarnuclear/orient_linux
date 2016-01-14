# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0060_auto_20160114_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodmap',
            name='control_rod_cluster',
        ),
        migrations.RemoveField(
            model_name='controlrodmap',
            name='control_rod_type',
        ),
        migrations.RemoveField(
            model_name='controlrodcluster',
            name='reactor_model',
        ),
        migrations.DeleteModel(
            name='ControlRodMap',
        ),
    ]
