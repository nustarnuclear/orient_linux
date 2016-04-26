# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0143_remove_fuelassemblyloadingpattern_control_rod_assembly'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='cluster',
        ),
        migrations.DeleteModel(
            name='ControlRodAssembly',
        ),
    ]
