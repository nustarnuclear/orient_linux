# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0049_remove_controlrodassembly_control_rod_map'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='basez',
        ),
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='primary',
        ),
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='step_size',
        ),
    ]
