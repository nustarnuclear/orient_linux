# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0053_auto_20160113_1537'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='burnablepoisonassemblyloadingpattern',
            options={},
        ),
        migrations.AddField(
            model_name='controlrodcluster',
            name='map',
            field=models.ManyToManyField(to='tragopan.ControlRodType', through='tragopan.ControlRodMap'),
        ),
    ]
