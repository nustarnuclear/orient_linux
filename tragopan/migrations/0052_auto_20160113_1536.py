# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0051_auto_20160113_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodmap',
            name='guide_tube_position',
        ),
        migrations.AddField(
            model_name='controlrodcluster',
            name='side_pin_num',
            field=models.PositiveSmallIntegerField(default=17),
        ),
    ]
