# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0002_auto_20151111_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelassemblyloadingpattern',
            name='following_index',
        ),
        migrations.RemoveField(
            model_name='fuelassemblyrepository',
            name='plant',
        ),
    ]
