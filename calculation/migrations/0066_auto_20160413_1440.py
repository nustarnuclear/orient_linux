# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0137_auto_20160413_1440'),
        ('calculation', '0065_auto_20160412_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreBaffleCalculation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('depletion_state', models.ForeignKey(to='calculation.DepletionState')),
                ('fuel_assembly_type', models.ForeignKey(to='tragopan.FuelAssemblyType')),
                ('pre_robin_model', models.ForeignKey(to='calculation.PreRobinModel')),
                ('reactor_model', models.OneToOneField(to='tragopan.ReactorModel')),
            ],
            options={
                'db_table': 'core_baffle_calculation',
            },
        ),
        migrations.AlterField(
            model_name='robintask',
            name='pre_robin_task',
            field=models.ForeignKey(to='calculation.PreRobinTask', null=True, blank=True, related_name='robin_tasks'),
        ),
        migrations.AddField(
            model_name='robintask',
            name='core_baffle_calc',
            field=models.ForeignKey(to='calculation.CoreBaffleCalculation', null=True, blank=True, related_name='baffle_tasks'),
        ),
    ]
