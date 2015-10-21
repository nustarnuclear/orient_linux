# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0104_auto_20151020_0339'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassembly',
            name='reator_model',
            field=models.ForeignKey(to='tragopan.ReactorModel', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fuelassemblyloadingpattern',
            name='rotation_degree',
            field=models.CharField(help_text='anticlokwise', choices=[('0', '0'), ('90', '90'), ('180', '180'), ('270', '270')], default='0', max_length=3),
        ),
    ]
