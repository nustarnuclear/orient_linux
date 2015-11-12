# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0006_remove_reactorposition_control_rod_mechanism'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassembly',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, to='tragopan.ControlRodCluster'),
        ),
    ]
