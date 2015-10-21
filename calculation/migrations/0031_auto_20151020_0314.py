# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0030_auto_20151020_0234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='result_xml',
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='result_path',
            field=models.FilePathField(max_length=200, blank=True, null=True, match='.*\\.xml$', recursive=True, path='/home/django/.django_project/media'),
        ),
    ]
