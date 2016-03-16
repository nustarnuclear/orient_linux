# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0053_auto_20160316_1033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='robinfile',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='robinfile',
            name='fuel_assembly_type',
        ),
        migrations.RemoveField(
            model_name='robinfile',
            name='plant',
        ),
        migrations.RemoveField(
            model_name='robinfile',
            name='user',
        ),
        migrations.DeleteModel(
            name='RobinFile',
        ),
    ]
