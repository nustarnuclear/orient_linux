# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0117_auto_20160316_1521'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitparameter',
            name='boron_density',
        ),
        migrations.RemoveField(
            model_name='unitparameter',
            name='fuel_temperature',
        ),
        migrations.RemoveField(
            model_name='unitparameter',
            name='moderator_temperature',
        ),
    ]
