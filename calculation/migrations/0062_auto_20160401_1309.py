# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0061_auto_20160401_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robintask',
            name='input_file',
            field=models.FileField(max_length=200, upload_to=calculation.models.get_robintask_upload_path),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
