# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0064_remove_multipleloadingpattern_from_database'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basefuel',
            name='axial_composition',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='plant',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='quadrant_four',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='quadrant_one',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='quadrant_three',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='quadrant_two',
        ),
        migrations.RemoveField(
            model_name='basefuel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='basefuelcomposition',
            name='base_fuel',
        ),
        migrations.RemoveField(
            model_name='basefuelcomposition',
            name='ibis',
        ),
        migrations.RemoveField(
            model_name='ibis',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='ibis',
            name='fuel_assembly_type',
        ),
        migrations.RemoveField(
            model_name='ibis',
            name='plant',
        ),
        migrations.RemoveField(
            model_name='ibis',
            name='reactor_model_id',
        ),
        migrations.RemoveField(
            model_name='ibis',
            name='user',
        ),
        migrations.DeleteModel(
            name='BaseFuel',
        ),
        migrations.DeleteModel(
            name='BaseFuelComposition',
        ),
        migrations.DeleteModel(
            name='Ibis',
        ),
    ]
