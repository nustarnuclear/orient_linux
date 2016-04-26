# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0136_reactormodel_dimension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reactormodel',
            name='dimension',
            field=models.PositiveSmallIntegerField(help_text='the maximum assembly number per dimension allowed', default=15),
        ),
    ]
