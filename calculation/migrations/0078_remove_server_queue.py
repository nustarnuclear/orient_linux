# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0077_prerobininput_boron_density'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='queue',
        ),
    ]
