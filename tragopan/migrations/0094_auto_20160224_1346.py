# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0093_grid_moderator_material'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='controlrodtype',
            options={},
        ),
        migrations.AlterField(
            model_name='controlrodtype',
            name='reactor_model',
            field=models.ForeignKey(blank=True, null=True, related_name='control_rod_types', to='tragopan.ReactorModel'),
        ),
        migrations.AlterField(
            model_name='wimsnuclidedata',
            name='id_wims',
            field=models.PositiveIntegerField(blank=True, unique=True, null=True),
        ),
    ]
