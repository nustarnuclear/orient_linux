# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0134_reactormodel_letter_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='default_step',
            field=models.PositiveSmallIntegerField(default=225),
        ),
        migrations.AddField(
            model_name='reactormodel',
            name='max_step',
            field=models.PositiveSmallIntegerField(default=228),
        ),
    ]
