# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0028_auto_20151229_1005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='material_type',
        ),
        migrations.AddField(
            model_name='material',
            name='basic_material',
            field=models.OneToOneField(to='tragopan.BasicMaterial', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, 'fuel by enrichment'), (2, 'by B10 linear density'), (3, 'blend basic materials'), (4, 'totally inherit from basic material')]),
        ),
    ]
