# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0023_remove_egrettask_result_xml'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='result_xml',
            field=models.FileField(blank=True, upload_to=calculation.models.get_egret_upload_path, null=True),
        ),
    ]
