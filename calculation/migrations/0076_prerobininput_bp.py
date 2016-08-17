# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0075_prerobininput_burnup_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobininput',
            name='bp',
            field=models.BooleanField(default=True, verbose_name='calculate bp out?'),
        ),
    ]
