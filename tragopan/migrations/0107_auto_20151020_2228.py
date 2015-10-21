# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0106_auto_20151020_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodassembly',
            name='fuel_assembly_model',
            field=models.ForeignKey(null=True, to='tragopan.FuelAssemblyModel', blank=True),
        ),
        migrations.AlterField(
            model_name='controlrodassembly',
            name='reactor_model',
            field=models.ForeignKey(null=True, to='tragopan.ReactorModel', related_name='control_rod_assemblies', blank=True),
        ),
        migrations.AlterField(
            model_name='controlrodassembly',
            name='type',
            field=models.CharField(max_length=8, choices=[('shutdown', 'shutdown'), ('adjust', 'adjust')], null=True, blank=True),
        ),
    ]
