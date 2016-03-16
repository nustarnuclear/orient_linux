# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0047_auto_20160310_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='robintask',
            name='pid',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
