# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0119_auto_20160316_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='reactor_model',
            field=models.ForeignKey(default=5, to='tragopan.ReactorModel'),
            preserve_default=False,
        ),
    ]
