# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0040_auto_20151229_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelElementRadialMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('radii', models.DecimalField(decimal_places=5, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7)),
            ],
            options={
                'db_table': 'fuel_element_radial_map',
            },
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='filling_gas_material',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='filling_gas_pressure',
        ),
        migrations.AddField(
            model_name='fuelelementradialmap',
            name='fuel_element',
            field=models.ForeignKey(to='tragopan.FuelElement'),
        ),
        migrations.AddField(
            model_name='fuelelementradialmap',
            name='material',
            field=models.ForeignKey(to='tragopan.Material'),
        ),
        migrations.AddField(
            model_name='fuelelement',
            name='radial_map',
            field=models.ManyToManyField(to='tragopan.Material', through='tragopan.FuelElementRadialMap'),
        ),
    ]
