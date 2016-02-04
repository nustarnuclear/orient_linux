# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0033_auto_20160201_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerobinbranch',
            name='default',
            field=models.BooleanField(help_text='set it as default', default=False),
        ),
        migrations.AlterField(
            model_name='prerobinmodel',
            name='default',
            field=models.BooleanField(help_text='set it as default', default=False),
        ),
    ]
