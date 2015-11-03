# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0035_multipleloadingpattern_from_database'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egretinputxml',
            name='basecore_path',
        ),
        migrations.AddField(
            model_name='egretinputxml',
            name='base_core_path',
            field=models.FilePathField(recursive=True, null=True, path='/home/django/.django_project/media', match='.*base_core\\.xml$', max_length=200, blank=True),
        ),
    ]
