# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0126_auto_20160328_1433'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='input_method',
        ),
        migrations.AddField(
            model_name='material',
            name='symbolic',
            field=models.BooleanField(default=False),
        ),
    ]
