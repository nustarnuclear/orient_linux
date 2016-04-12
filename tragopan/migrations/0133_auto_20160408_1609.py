# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0132_remove_controlrodassemblytype_step_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='clockwise_increase',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='set_zero_to_direction',
            field=models.CharField(default='E', choices=[('E', 'East'), ('S', 'South'), ('W', 'West'), ('N', 'North')], max_length=1),
        ),
    ]
