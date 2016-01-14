# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0056_remove_controlrodcluster_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlRodAssemblyMap',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('row', models.PositiveSmallIntegerField()),
                ('column', models.PositiveSmallIntegerField()),
            ],
            options={
                'db_table': 'control_rod_assembly_map',
            },
        ),
        migrations.CreateModel(
            name='ControlRodAssemblyType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('basez', models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=5, help_text='unit:cm', null=True, blank=True)),
                ('step_size', models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=5, help_text='unit:cm', null=True, blank=True)),
                ('side_pin_num', models.PositiveSmallIntegerField(default=17)),
                ('map', models.ManyToManyField(to='tragopan.ControlRodType', through='tragopan.ControlRodAssemblyMap')),
            ],
            options={
                'db_table': 'control_rod_assembly_type',
            },
        ),
        migrations.AddField(
            model_name='controlrodassemblymap',
            name='control_rod_assembly_type',
            field=models.ForeignKey(to='tragopan.ControlRodAssemblyType', related_name='control_rod_pos'),
        ),
        migrations.AddField(
            model_name='controlrodassemblymap',
            name='control_rod_type',
            field=models.ForeignKey(to='tragopan.ControlRodType'),
        ),
    ]
