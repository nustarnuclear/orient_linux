# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0083_remove_burnablepoisonsection_transection'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelElementSection',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('section_num', models.PositiveSmallIntegerField()),
                ('length', models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=3, help_text='unit:cm')),
            ],
            options={
                'db_table': 'fuel_element_section',
            },
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='coated',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='coating_bottom',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='coating_material',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='coating_thickness',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='coating_top',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='filling_gas_material',
        ),
        migrations.RemoveField(
            model_name='fuelelement',
            name='plenum_length',
        ),
        migrations.AddField(
            model_name='fuelelementsection',
            name='fuel_element',
            field=models.ForeignKey(related_name='sections', to='tragopan.FuelElement'),
        ),
        migrations.AddField(
            model_name='fuelelementsection',
            name='material_transection',
            field=models.ForeignKey(to='tragopan.MaterialTransection'),
        ),
    ]
