# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0018_auto_20150922_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='task_type',
            field=models.CharField(default='customize', max_length=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='restart_file',
            field=models.FilePathField(recursive=True, blank=True, null=True, path='/home/django/.django_project/media'),
        ),
    ]
