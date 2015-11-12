# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0003_auto_20151111_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlRodCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('cluster_name', models.CharField(max_length=5)),
                ('reactor_model', models.ForeignKey(to='tragopan.ReactorModel')),
            ],
            options={
                'db_table': 'control_rod_cluster',
            },
        ),
    ]
