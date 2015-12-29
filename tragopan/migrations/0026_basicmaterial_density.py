# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0025_auto_20151228_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicmaterial',
            name='density',
            field=models.DecimalField(default=0, decimal_places=8, help_text='unit:g/cm3', max_digits=15),
            preserve_default=False,
        ),
    ]
