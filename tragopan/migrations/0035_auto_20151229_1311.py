# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0034_auto_20151229_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mixturecomposition',
            name='volume_percent',
        ),
        migrations.AddField(
            model_name='mixturecomposition',
            name='input_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'by weight'), (2, 'by volume')], default=1),
        ),
    ]
