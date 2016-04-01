# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0125_remove_reactormodel_boron_density'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='density_percent',
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Compound or elementary substance'), (2, 'alloy')]),
        ),
    ]
