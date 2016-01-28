# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0025_auto_20160125_1050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobininput',
            name='branch_composition',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='core_baffle',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='fuel_assembly_type',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='grid',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='plant',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='pre_robin_model',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='use_pre_segment',
        ),
        migrations.RemoveField(
            model_name='prerobininput',
            name='user',
        ),
        migrations.DeleteModel(
            name='PreRobinInput',
        ),
    ]
