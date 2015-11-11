# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0006_auto_20151110_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='ibis',
            name='ibis_path',
            field=models.FilePathField(blank=True, max_length=200, recursive=True, null=True, match='.*\\.TAB$', path='/home/django/.django_project/media'),
        ),
    ]
