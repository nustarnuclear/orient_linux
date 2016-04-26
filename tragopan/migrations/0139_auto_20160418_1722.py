# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tragopan.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0138_auto_20160413_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='corebaffle',
            name='bottom_gap',
            field=models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', default=3.112, decimal_places=3),
        ),
        migrations.AddField(
            model_name='corebaffle',
            name='bottom_material',
            field=models.ForeignKey(to='tragopan.Material', default=tragopan.models.bottom_material_default, related_name='bottom_core_baffels'),
        ),
        migrations.AddField(
            model_name='corebaffle',
            name='top_material',
            field=models.ForeignKey(to='tragopan.Material', default=tragopan.models.top_material_default, related_name='top_core_baffels'),
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Compound or elementary substance'), (2, 'alloy'), (3, 'symbolic')], default=1),
        ),
        migrations.AlterField(
            model_name='corebaffle',
            name='vendor',
            field=models.ForeignKey(null=True, to='tragopan.Vendor', blank=True),
        ),
    ]
