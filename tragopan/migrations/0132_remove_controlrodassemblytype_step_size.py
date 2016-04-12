# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0131_reactormodel_control_rod_step_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassemblytype',
            name='step_size',
        ),
    ]
