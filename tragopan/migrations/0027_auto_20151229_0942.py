# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0026_basicmaterial_density'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicmaterial',
            name='density',
            field=models.DecimalField(blank=True, null=True, decimal_places=8, help_text='unit:g/cm3', max_digits=15),
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Compound or elementary substance'), (2, 'mixture'), (3, 'symbolic')]),
        ),
    ]
