# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0008_remove_controlrodassembly_cluster_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodassemblyloadingpattern',
            name='control_rod_assembly',
            field=models.ForeignKey(related_name='loading_patterns', to='tragopan.ControlRodAssembly'),
        ),
        migrations.AlterField(
            model_name='controlrodassemblystep',
            name='control_rod_assembly',
            field=models.ForeignKey(to='tragopan.ControlRodCluster'),
        ),
        migrations.AlterField(
            model_name='operationparameter',
            name='control_rod_step',
            field=models.ManyToManyField(to='tragopan.ControlRodCluster', through='tragopan.ControlRodAssemblyStep'),
        ),
    ]
