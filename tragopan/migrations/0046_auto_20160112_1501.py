# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0045_auto_20160112_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodtype',
            name='absorb_diameter',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='absorb_length',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='absorb_material',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='cladding_inner_diameter',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='cladding_material',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='cladding_outer_diameter',
        ),
        migrations.RemoveField(
            model_name='controlrodtype',
            name='fuel_assembly_model',
        ),
        migrations.AddField(
            model_name='controlrodtype',
            name='active_length',
            field=models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], null=True, decimal_places=3, blank=True, help_text='unit:cm'),
        ),
        migrations.AddField(
            model_name='controlrodtype',
            name='reactor_model',
            field=models.ForeignKey(null=True, to='tragopan.ReactorModel', blank=True),
        ),
    ]
