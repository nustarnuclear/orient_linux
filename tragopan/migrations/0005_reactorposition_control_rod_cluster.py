# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0004_controlrodcluster'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactorposition',
            name='control_rod_cluster',
            field=models.ForeignKey(blank=True, null=True, related_name='positions', related_query_name='position', to='tragopan.ControlRodCluster'),
        ),
    ]
