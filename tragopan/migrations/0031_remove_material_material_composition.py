# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0030_auto_20151229_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='material_composition',
        ),
    ]
