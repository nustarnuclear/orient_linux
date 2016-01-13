# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0044_auto_20160112_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlRodRadialMap',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('radii', models.DecimalField(help_text='unit:cm', decimal_places=5, max_digits=7, validators=[django.core.validators.MinValueValidator(0)])),
                ('control_rod', models.ForeignKey(to='tragopan.ControlRodType', related_name='materials')),
                ('material', models.ForeignKey(to='tragopan.Material')),
            ],
            options={
                'db_table': 'control_rod_radial_map',
            },
        ),
        migrations.AlterField(
            model_name='burnablepoisonmaterial',
            name='burnable_poison_rod',
            field=models.ForeignKey(to='tragopan.BurnablePoisonRod', related_name='radial_materials'),
        ),
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='fuel_assembly_model',
            field=models.OneToOneField(to='tragopan.FuelAssemblyModel', related_name='bp_rod'),
        ),
        migrations.AlterField(
            model_name='guidetube',
            name='buffer_inner_diameter',
            field=models.DecimalField(help_text='unit:cm', blank=True, null=True, decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='guidetube',
            name='buffer_outer_diameter',
            field=models.DecimalField(help_text='unit:cm', blank=True, null=True, decimal_places=3, max_digits=7, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='controlrodtype',
            name='radial_map',
            field=models.ManyToManyField(through='tragopan.ControlRodRadialMap', to='tragopan.Material'),
        ),
    ]
