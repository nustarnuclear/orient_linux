# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0059_controlrodcluster_control_rod_assembly_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodcluster',
            name='basez',
        ),
        migrations.RemoveField(
            model_name='controlrodcluster',
            name='side_pin_num',
        ),
        migrations.RemoveField(
            model_name='controlrodcluster',
            name='step_size',
        ),
    ]
