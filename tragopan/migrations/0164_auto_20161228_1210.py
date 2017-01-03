# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tragopan.models


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0163_fuelassemblytype_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='aosc_file',
            field=models.FileField(null=True, blank=True, upload_to=tragopan.models.get_drwm_file_path),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='aosc_file_format',
            field=models.SmallIntegerField(choices=[(0, 'Decimal'), (1, 'Binary')], default=1),
        ),
    ]
