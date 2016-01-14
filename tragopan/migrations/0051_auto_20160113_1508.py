# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0050_auto_20160113_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodmap',
            name='control_rod_cluster',
            field=models.ForeignKey(to='tragopan.ControlRodCluster', default=1, related_name='control_rods'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='controlrodmap',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='controlrodmap',
            name='control_rod_assembly',
        ),
    ]
