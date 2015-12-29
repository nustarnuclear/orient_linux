# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0031_remove_material_material_composition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='materialcomposition',
            name='material_id',
        ),
        migrations.RemoveField(
            model_name='materialcomposition',
            name='wims_element_data_id',
        ),
        migrations.DeleteModel(
            name='MaterialComposition',
        ),
    ]
