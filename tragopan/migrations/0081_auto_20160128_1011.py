# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0080_auto_20160127_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialTransection',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('radius', models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=5)),
            ],
            options={
                'db_table': 'material_transection',
            },
        ),
        migrations.CreateModel(
            name='TransectionMaterial',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('layer_num', models.PositiveSmallIntegerField()),
                ('radius', models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=5)),
                ('material', models.ForeignKey(to='tragopan.Material')),
                ('transection', models.ForeignKey(related_name='radial_materials', to='tragopan.MaterialTransection')),
            ],
            options={
                'db_table': 'transection_material',
            },
        ),
        migrations.AddField(
            model_name='materialtransection',
            name='radial_map',
            field=models.ManyToManyField(through='tragopan.TransectionMaterial', to='tragopan.Material'),
        ),
    ]
