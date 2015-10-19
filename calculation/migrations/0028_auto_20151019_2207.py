# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0027_basefuel_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='egretinputxml',
            name='base_component_path',
            field=models.FilePathField(blank=True, path='/home/django/.django_project/media', max_length=200, null=True, recursive=True),
        ),
        migrations.AddField(
            model_name='egretinputxml',
            name='basecore_path',
            field=models.FilePathField(blank=True, path='/home/django/.django_project/media', max_length=200, null=True, recursive=True),
        ),
        migrations.AddField(
            model_name='egretinputxml',
            name='loading_pattern_path',
            field=models.FilePathField(blank=True, path='/home/django/.django_project/media', max_length=200, null=True, recursive=True),
        ),
        migrations.AlterField(
            model_name='basefuel',
            name='axial_composition',
            field=models.ManyToManyField(to='calculation.Ibis', related_name='base_fuels', through='calculation.BaseFuelComposition'),
        ),
        migrations.AlterField(
            model_name='basefuelcomposition',
            name='ibis',
            field=models.ForeignKey(to='calculation.Ibis', related_name='base_fuel_compositions'),
        ),
    ]
