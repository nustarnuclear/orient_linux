# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0012_auto_20151111_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodassembly',
            name='cluster',
            field=models.ForeignKey(blank=True, to='tragopan.ControlRodCluster', related_name='control_rod_assemblies', null=True),
        ),
        migrations.AlterOrderWithRespectTo(
            name='cycle',
            order_with_respect_to='unit',
        ),
    ]
