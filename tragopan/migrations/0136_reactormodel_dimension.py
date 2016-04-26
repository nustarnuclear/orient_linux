# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0135_auto_20160408_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='dimension',
            field=models.PositiveSmallIntegerField(default=15, help_text='the maximum assembly per dimension allowed'),
        ),
    ]
