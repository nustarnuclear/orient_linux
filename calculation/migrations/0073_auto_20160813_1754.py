# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0072_auto_20160813_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='calculation_identity',
        ),
        migrations.AddField(
            model_name='egrettask',
            name='server',
            field=models.ForeignKey(null=True, blank=True, to='calculation.Server'),
        ),
    ]
