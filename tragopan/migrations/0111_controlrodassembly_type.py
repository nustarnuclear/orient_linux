# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0110_remove_controlrodassembly_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassembly',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'black rod'), (2, 'grep rod')], default=1),
        ),
    ]
