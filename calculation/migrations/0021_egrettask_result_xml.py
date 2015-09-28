# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0020_egrettask_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='result_xml',
            field=models.FilePathField(blank=True, path='/home/django/.django_project/media', recursive=True, null=True),
        ),
    ]
