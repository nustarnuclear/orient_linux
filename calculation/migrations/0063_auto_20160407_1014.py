# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0062_auto_20160401_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robintask',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]
