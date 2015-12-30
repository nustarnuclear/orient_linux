# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0035_auto_20151229_1311'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mixturecomposition',
            old_name='weight_percent',
            new_name='percent',
        ),
    ]
