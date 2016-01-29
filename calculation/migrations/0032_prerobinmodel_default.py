# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0031_auto_20160129_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobinmodel',
            name='default',
            field=models.BooleanField(default=False, help_text='set it as default'),
        ),
    ]
