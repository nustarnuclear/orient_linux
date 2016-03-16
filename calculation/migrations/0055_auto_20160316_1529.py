# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0117_auto_20160316_1521'),
        ('calculation', '0054_auto_20160316_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='default',
        ),
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='unit',
        ),
        migrations.AddField(
            model_name='prerobinbranch',
            name='reactor_model',
            field=models.OneToOneField(default=5, to='tragopan.ReactorModel'),
            preserve_default=False,
        ),
    ]
