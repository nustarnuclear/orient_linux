# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0032_auto_20151229_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='input_method',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'fuel by enrichment'), (2, 'by B10 linear density'), (3, 'blend basic materials'), (4, 'totally inherit from basic material')]),
        ),
    ]
