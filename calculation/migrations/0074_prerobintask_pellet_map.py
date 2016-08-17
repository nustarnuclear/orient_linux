# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0073_auto_20160813_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='pellet_map',
            field=models.CommaSeparatedIntegerField(help_text='pellet pk', blank=True, max_length=256, null=True),
        ),
    ]
