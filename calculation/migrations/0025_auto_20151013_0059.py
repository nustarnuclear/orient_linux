# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0024_egrettask_result_xml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='egretinputxml',
            name='base_component_xml',
            field=models.FileField(upload_to=calculation.models.get_egret_input_xml_path),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='base_core_xml',
            field=models.FileField(upload_to=calculation.models.get_egret_input_xml_path),
        ),
        migrations.AlterField(
            model_name='egretinputxml',
            name='loading_pattern_xml',
            field=models.FileField(upload_to=calculation.models.get_egret_input_xml_path),
        ),
    ]
