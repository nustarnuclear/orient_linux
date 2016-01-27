# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0070_burnablepoisonsection_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonmaterial',
            name='burnable_poison_rod',
        ),
        migrations.RemoveField(
            model_name='burnablepoisonrod',
            name='radial_map',
        ),
        migrations.AlterField(
            model_name='burnablepoisonmaterial',
            name='section',
            field=models.ForeignKey(to='tragopan.BurnablePoisonSection'),
        ),
    ]
