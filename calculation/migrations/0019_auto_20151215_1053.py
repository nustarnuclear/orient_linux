# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0018_remove_egrettask_result_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='base_component_path',
            field=models.FilePathField(path='/var/lib/orient/media', blank=True, max_length=200, null=True, recursive=True, match='.*base_component\\.xml$'),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='base_core_path',
            field=models.FilePathField(path='/var/lib/orient/media', blank=True, max_length=200, null=True, recursive=True, match='.*base_core\\.xml$'),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='loading_pattern_path',
            field=models.FilePathField(path='/var/lib/orient/media', blank=True, max_length=200, null=True, recursive=True, match='.*loading_pattern\\.xml$'),
        ),
        migrations.AlterField(
            model_name='ibis',
            name='ibis_path',
            field=models.FilePathField(path='/var/lib/orient/media', blank=True, max_length=200, null=True, recursive=True, match='.*\\.TAB$'),
        ),
    ]
