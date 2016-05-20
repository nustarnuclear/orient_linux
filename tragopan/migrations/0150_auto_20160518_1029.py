# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0149_auto_20160516_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reactormodel',
            name='drwm_file_format',
            field=models.SmallIntegerField(choices=[(0, 'Decimal'), (1, 'Binary')], default=1),
        ),
    ]
