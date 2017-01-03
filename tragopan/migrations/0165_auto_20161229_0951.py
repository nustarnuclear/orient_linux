# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tragopan.models


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0164_auto_20161228_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='aosc_wgt_func_file',
            field=models.FileField(blank=True, upload_to=tragopan.models.get_drwm_file_path, null=True, help_text='weight function file'),
        ),
        migrations.AlterField(
            model_name='reactormodel',
            name='aosc_file',
            field=models.FileField(blank=True, upload_to=tragopan.models.get_drwm_file_path, null=True, help_text='detector response file'),
        ),
    ]
