# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0058_controlrodassemblytype_reactor_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodcluster',
            name='control_rod_assembly_type',
            field=models.ForeignKey(to='tragopan.ControlRodAssemblyType', default=1, related_name='control_rod_clusters'),
            preserve_default=False,
        ),
    ]
