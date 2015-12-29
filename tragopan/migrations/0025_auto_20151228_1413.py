# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0024_auto_20151228_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicElementComposition',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('weight_percent', models.DecimalField(decimal_places=6, null=True, help_text='unit:%', blank=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], max_digits=9)),
                ('element_number', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'basoc_element_composition',
            },
        ),
        migrations.CreateModel(
            name='BasicMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('name', models.CharField(max_length=8)),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(1, 'Compound or elementary substance'), (2, 'mixture')])),
                ('composition', models.ManyToManyField(to='tragopan.WmisElementData', through='tragopan.BasicElementComposition')),
            ],
            options={
                'db_table': 'basic_material',
            },
        ),
        migrations.AddField(
            model_name='basicelementcomposition',
            name='basic_material',
            field=models.ForeignKey(to='tragopan.BasicMaterial', related_name='elements'),
        ),
        migrations.AddField(
            model_name='basicelementcomposition',
            name='wims_element',
            field=models.ForeignKey(to='tragopan.WmisElementData'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='basicelementcomposition',
            order_with_respect_to='basic_material',
        ),
    ]
