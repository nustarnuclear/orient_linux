# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tragopan.models


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0148_auto_20160505_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='drwm_file',
            field=models.FileField(upload_to=tragopan.models.get_drwm_file_path, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='drwm_file_format',
            field=models.SmallIntegerField(choices=[(0, 'Binary'), (1, 'Decimal')], default=1),
        ),
        migrations.AddField(
            model_name='unitparameter',
            name='num_dsf',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='unitparameter',
            name='num_signal',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='fuelassemblymodel',
            name='name',
            field=models.CharField(max_length=5),
        ),
    ]
