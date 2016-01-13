# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0047_auto_20160112_1712'),
        ('calculation', '0022_auto_20160112_1712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prerobinbranch',
            name='reactor_model',
        ),
        migrations.AddField(
            model_name='prerobinbranch',
            name='unit',
            field=models.ForeignKey(to='tragopan.UnitParameter', related_name='branches', default=1),
            preserve_default=False,
        ),
    ]
