# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0102_auto_20160304_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reactormodel',
            name='cold_state_assembly_pitch',
        ),
        migrations.RemoveField(
            model_name='reactormodel',
            name='hot_state_assembly_pitch',
        ),
    ]
