# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0011_auto_20151113_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='egrettask',
            name='loading_pattern',
            field=models.ForeignKey(to='calculation.MultipleLoadingPattern'),
        ),
    ]
