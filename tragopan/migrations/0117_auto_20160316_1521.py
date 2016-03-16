# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0116_controlrodassemblytype_overall_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='boron_density',
            field=models.PositiveSmallIntegerField(help_text='ppm', default=500),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='fuel_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=903),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='moderator_temperature',
            field=models.PositiveSmallIntegerField(help_text='K', default=577),
        ),
    ]
