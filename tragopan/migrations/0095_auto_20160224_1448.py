# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0094_auto_20160224_1346'),
    ]

    operations = [
        migrations.RenameField(
            model_name='material',
            old_name='mixture_composition',
            new_name='volume_composition',
        ),
        migrations.AddField(
            model_name='material',
            name='density',
            field=models.DecimalField(decimal_places=8, help_text='unit:g/cm3', blank=True, null=True, max_digits=15),
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'fuel by enrichment'), (2, 'blend materials by B10 linear density'), (3, 'blend materials by volume percent'), (4, 'totally inherit from basic material'), (5, 'inherit from basic material with B10 linear density'), (6, 'blend materials by weight percent')], default=1),
        ),
    ]
