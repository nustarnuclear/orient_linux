# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0052_auto_20160113_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodmap',
            name='column',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlrodmap',
            name='row',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
