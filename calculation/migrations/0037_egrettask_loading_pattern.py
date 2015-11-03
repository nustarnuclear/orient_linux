# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0036_auto_20151104_0257'),
    ]

    operations = [
        migrations.AddField(
            model_name='egrettask',
            name='loading_pattern',
            field=models.ForeignKey(blank=True, null=True, to='calculation.MultipleLoadingPattern'),
        ),
    ]
