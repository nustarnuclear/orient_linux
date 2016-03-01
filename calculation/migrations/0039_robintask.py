# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0038_auto_20160225_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='RobinTask',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('input_file', models.FileField(upload_to=calculation.models.get_robintask_upload_path)),
                ('task_status', models.PositiveSmallIntegerField(choices=[(0, 'waiting'), (1, 'calculating'), (2, 'suspended'), (3, 'stopped'), (4, 'finished'), (5, 'cancled'), (6, 'errored')], default=0)),
                ('pre_robin_model', models.ForeignKey(to='calculation.PreRobinTask')),
            ],
            options={
                'db_table': 'robin_task',
            },
        ),
    ]
