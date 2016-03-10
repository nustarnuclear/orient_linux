# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0045_server_queue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='status',
        ),
        migrations.AddField(
            model_name='robintask',
            name='log_file',
            field=models.FileField(upload_to=calculation.models.get_robintask_upload_path, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='robintask',
            name='output_file',
            field=models.FileField(upload_to=calculation.models.get_robintask_upload_path, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='server',
            field=models.ForeignKey(to='calculation.Server', default=calculation.models.server_default, related_name='pre_robin_inputs'),
        ),
    ]
