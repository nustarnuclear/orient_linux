# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0028_auto_20151019_2207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egretinputxml',
            name='base_component_xml',
        ),
        migrations.RemoveField(
            model_name='egretinputxml',
            name='base_core_xml',
        ),
        migrations.RemoveField(
            model_name='egretinputxml',
            name='loading_pattern_xml',
        ),
    ]
