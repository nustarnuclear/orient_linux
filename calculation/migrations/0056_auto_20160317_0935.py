# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0055_auto_20160316_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='server',
            options={'ordering': ['IP']},
        ),
    ]
