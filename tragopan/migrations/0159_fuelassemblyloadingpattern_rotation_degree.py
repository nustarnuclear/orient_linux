# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0158_auto_20160612_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelassemblyloadingpattern',
            name='rotation_degree',
            field=models.PositiveSmallIntegerField(choices=[(1, '0'), (2, '90'), (3, '180'), (4, '270')], help_text='anticlokwise', default=1),
        ),
    ]
