# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0027_prerobininput'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobintask',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='prerobintask',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='prerobintask',
            name='fuel_assembly_type',
        ),
        migrations.RemoveField(
            model_name='prerobintask',
            name='user',
        ),
        migrations.DeleteModel(
            name='PreRobinTask',
        ),
    ]
