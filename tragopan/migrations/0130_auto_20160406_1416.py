# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0129_auto_20160406_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassemblyloadingpattern',
            name='control_rod_assembly',
        ),
        migrations.RemoveField(
            model_name='controlrodassemblyloadingpattern',
            name='cycle',
        ),
        migrations.RemoveField(
            model_name='controlrodassemblyloadingpattern',
            name='reactor_position',
        ),
        migrations.DeleteModel(
            name='ControlRodAssemblyLoadingPattern',
        ),
    ]
