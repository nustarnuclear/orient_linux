# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0141_auto_20160419_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblyloadingpattern',
            name='cr_out',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Compound or elementary substance'), (2, 'alloy')], default=1),
        ),
    ]
