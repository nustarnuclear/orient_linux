# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0066_auto_20160413_1440'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corebafflecalculation',
            name='depletion_state',
        ),
    ]
