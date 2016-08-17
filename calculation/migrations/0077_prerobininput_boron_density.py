# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0076_prerobininput_bp'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobininput',
            name='boron_density',
            field=models.PositiveSmallIntegerField(help_text='ppm', default=500),
        ),
    ]
