# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0043_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobintask',
            name='server',
            field=models.ForeignKey(to='calculation.Server', default=calculation.models.server_default),
        ),
        migrations.AlterField(
            model_name='server',
            name='IP',
            field=models.GenericIPAddressField(unique=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='status',
            field=models.CharField(choices=[('A', 'available'), ('B', 'busy')], default='A', max_length=1),
        ),
    ]
