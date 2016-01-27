# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0064_auto_20160125_1050'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calculation', '0024_prerobinbranch_max_burnup_point'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreRobinTask',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('task_name', models.CharField(max_length=32)),
                ('height', models.DecimalField(max_digits=10, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, help_text='cm')),
            ],
            options={
                'db_table': 'pre_robin_task',
            },
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='max_moderator_temperature',
            field=models.PositiveSmallIntegerField(default=615, help_text='K'),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='min_moderator_temperature',
            field=models.PositiveSmallIntegerField(default=561, help_text='K'),
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='branch',
            field=models.ForeignKey(to='calculation.PreRobinBranch'),
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='burnable_poison_assembly',
            field=models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='fuel_assembly_type',
            field=models.ForeignKey(to='tragopan.FuelAssemblyType'),
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
    ]
