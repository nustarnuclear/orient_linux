# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0089_controlrodsection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodtype',
            name='radial_map',
        ),
    ]
