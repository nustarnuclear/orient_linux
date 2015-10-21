# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0029_auto_20151019_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='result_path',
            field=models.FilePathField(path='/home/django/.django_project/media', null=True, recursive=True, max_length=200, match='.*\\.workspace\\.*\\.xml$', blank=True),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='base_component_path',
            field=models.FilePathField(path='/home/django/.django_project/media', null=True, recursive=True, max_length=200, match='.*base_component\\.xml$', blank=True),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='basecore_path',
            field=models.FilePathField(path='/home/django/.django_project/media', null=True, recursive=True, max_length=200, match='.*basecore\\.xml$', blank=True),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='loading_pattern_path',
            field=models.FilePathField(path='/home/django/.django_project/media', null=True, recursive=True, max_length=200, match='.*loading_pattern\\.xml$', blank=True),
        ),
    ]
