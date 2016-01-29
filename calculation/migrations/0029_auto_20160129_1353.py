# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calculation', '0028_auto_20160129_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepletionState',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('system_pressure', models.DecimalField(default=15.51, help_text='MPa', max_digits=7, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5)),
                ('burnup_point', models.DecimalField(default=60, help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100', max_digits=7, validators=[django.core.validators.MaxValueValidator(0)], decimal_places=4)),
                ('burnup_unit', models.PositiveSmallIntegerField(default=1, choices=[(1, 'GWd/tU'), (2, 'DGWd/tU'), (3, 'day'), (4, 'Dday')])),
                ('fuel_temperature', models.PositiveSmallIntegerField(help_text='K')),
                ('moderator_temperature', models.PositiveSmallIntegerField(help_text='K')),
                ('boron_density', models.PositiveSmallIntegerField(help_text='ppm')),
                ('dep_strategy', models.CharField(default='LLR', max_length=3, choices=[('LLR', 'LLR'), ('PPC', 'PPC'), ('LR', 'LR'), ('PC', 'PC')])),
                ('power_density', models.DecimalField(help_text='unit:w/g', max_digits=15, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5)),
            ],
            options={
                'db_table': 'depletion_state',
            },
        ),
        migrations.CreateModel(
            name='PreRobinTask',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('pin_map', models.CommaSeparatedIntegerField(max_length=256)),
                ('fuel_map', models.CommaSeparatedIntegerField(max_length=256)),
                ('branch', models.ForeignKey(to='calculation.PreRobinBranch')),
                ('depletion_state', models.ForeignKey(to='calculation.DepletionState')),
            ],
            options={
                'db_table': 'pre_robin_task',
            },
        ),
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='dep_strategy',
        ),
        migrations.RemoveField(
            model_name='prerobinmodel',
            name='system_pressure',
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='pre_robin_model',
            field=models.ForeignKey(to='calculation.PreRobinModel'),
        ),
        migrations.AddField(
            model_name='prerobintask',
            name='user',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
