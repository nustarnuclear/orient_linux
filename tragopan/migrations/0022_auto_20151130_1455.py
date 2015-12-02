# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tragopan.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0021_auto_20151113_1654'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperationBankPosition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('step', models.DecimalField(decimal_places=5, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('control_rod_cluster', models.ForeignKey(to='tragopan.ControlRodCluster')),
            ],
            options={
                'db_table': 'operation_bank_position',
            },
        ),
        migrations.CreateModel(
            name='OperationDistributionData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('relative_power', models.DecimalField(decimal_places=9, max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('FDH', models.DecimalField(decimal_places=5, help_text='unit:', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('axial_power_shift', models.DecimalField(decimal_places=6, help_text='unit:%FP', max_digits=9, blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(-100)])),
            ],
            options={
                'db_table': 'operation_distribution_data',
            },
        ),
        migrations.CreateModel(
            name='OperationMonthlyParameter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('date', models.DateField(blank=True, null=True, help_text='Please use <b>YYYY-MM-DD<b> to input the date')),
                ('avg_burnup', models.DecimalField(blank=True, decimal_places=5, help_text='unit:MWd/tU', max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('relative_power', models.DecimalField(blank=True, decimal_places=9, max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('boron_concentration', models.DecimalField(blank=True, decimal_places=5, help_text='unit:ppm', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('axial_power_shift', models.DecimalField(decimal_places=6, help_text='unit:%FP', max_digits=9, blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(-100)])),
                ('FQ', models.DecimalField(blank=True, decimal_places=5, help_text='unit:', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('raw_file', models.FileField(upload_to=tragopan.models.get_monthly_data_upload_path)),
                ('bank_position', models.ManyToManyField(through='tragopan.OperationBankPosition', to='tragopan.ControlRodCluster')),
                ('cycle', models.ForeignKey(to='tragopan.Cycle')),
                ('distribution', models.ManyToManyField(through='tragopan.OperationDistributionData', to='tragopan.ReactorPosition')),
            ],
            options={
                'db_table': 'operation_monthly_parameter',
            },
        ),
        migrations.AddField(
            model_name='operationdistributiondata',
            name='operation',
            field=models.ForeignKey(to='tragopan.OperationMonthlyParameter'),
        ),
        migrations.AddField(
            model_name='operationdistributiondata',
            name='reactor_position',
            field=models.ForeignKey(to='tragopan.ReactorPosition'),
        ),
        migrations.AddField(
            model_name='operationbankposition',
            name='operation',
            field=models.ForeignKey(to='tragopan.OperationMonthlyParameter'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='operationmonthlyparameter',
            order_with_respect_to='cycle',
        ),
        migrations.AlterOrderWithRespectTo(
            name='operationdistributiondata',
            order_with_respect_to='operation',
        ),
        migrations.AlterOrderWithRespectTo(
            name='operationbankposition',
            order_with_respect_to='operation',
        ),
    ]
