# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0047_auto_20160112_1712'),
        ('calculation', '0021_auto_20160105_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='control_rod_assembly',
        ),
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='identity',
        ),
        migrations.AddField(
            model_name='prerobinbranch',
            name='reactor_model',
            field=models.ForeignKey(default=1, to='tragopan.ReactorModel', related_name='branches'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='boron_density_interval',
            field=models.PositiveSmallIntegerField(help_text='ppm', default=200),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='fuel_temperature_interval',
            field=models.PositiveSmallIntegerField(help_text='K', default=50),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='max_boron_density',
            field=models.PositiveSmallIntegerField(help_text='ppm', default=2000),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='max_fuel_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=1253),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='max_moderator_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=561),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='min_boron_density',
            field=models.PositiveSmallIntegerField(help_text='ppm', default=0),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='min_fuel_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=553),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='min_moderator_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=615),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='moderator_temperature_interval',
            field=models.PositiveSmallIntegerField(help_text='K', default=4),
        ),
        migrations.AlterField(
            model_name='prerobinbranch',
            name='shutdown_cooling_days',
            field=models.PositiveSmallIntegerField(help_text='day', default=3000),
        ),
    ]
