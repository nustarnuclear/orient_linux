# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0109_auto_20160307_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mixturecomposition',
            name='material',
        ),
        migrations.RemoveField(
            model_name='mixturecomposition',
            name='mixture',
        ),
        migrations.DeleteModel(
            name='MixtureComposition',
        ),
    ]
