# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tragopan', '0086_auto_20160128_1506'),
        ('calculation', '0026_auto_20160128_1440'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreRobinInput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('burnable_poison_assembly', models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True)),
                ('fuel_assembly_type', models.ForeignKey(to='tragopan.FuelAssemblyType')),
                ('unit', models.ForeignKey(to='tragopan.UnitParameter')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'db_table': 'pre_robin_input',
            },
        ),
    ]
