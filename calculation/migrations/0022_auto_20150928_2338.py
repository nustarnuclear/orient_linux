# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0021_egrettask_result_xml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='egrettask',
            name='restart_file',
            field=models.FilePathField(blank=True, null=True, recursive=True, max_length=200, path='/home/django/.django_project/media'),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='result_xml',
            field=models.FilePathField(blank=True, null=True, recursive=True, max_length=200, path='/home/django/.django_project/media'),
        ),
    ]
