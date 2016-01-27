# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0063_auto_20160114_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodcluster',
            name='control_rod_assembly_type',
            field=models.ForeignKey(related_name='clusters', to='tragopan.ControlRodAssemblyType'),
        ),
    ]
