# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0019_auto_20151113_1649'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlRodAssemblyStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('step', models.DecimalField(max_digits=10, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('control_rod_cluster', models.ForeignKey(to='tragopan.ControlRodCluster')),
            ],
            options={
                'db_table': 'control_rod_assembly_step',
            },
        ),
        migrations.CreateModel(
            name='OperationDailyParameter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('date', models.DateField(blank=True, null=True, help_text='Please use <b>YYYY-MM-DD<b> to input the date')),
                ('burnup', models.DecimalField(max_digits=15, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:MWd/tU')),
                ('relative_power', models.DecimalField(max_digits=10, decimal_places=9, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('critical_boron_density', models.DecimalField(max_digits=10, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:ppm')),
                ('axial_power_shift', models.DecimalField(max_digits=9, blank=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(-100)], decimal_places=6, null=True, help_text='unit:%FP')),
                ('control_rod_step', models.ManyToManyField(to='tragopan.ControlRodCluster', through='tragopan.ControlRodAssemblyStep')),
                ('cycle', models.ForeignKey(to='tragopan.Cycle')),
            ],
            options={
                'db_table': 'operation_parameter',
            },
        ),
        migrations.AddField(
            model_name='controlrodassemblystep',
            name='operation',
            field=models.ForeignKey(to='tragopan.OperationDailyParameter'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='operationdailyparameter',
            order_with_respect_to='cycle',
        ),
    ]
