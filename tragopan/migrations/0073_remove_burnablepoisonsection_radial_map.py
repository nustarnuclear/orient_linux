# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0072_auto_20160127_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonsection',
            name='radial_map',
        ),
    ]
