# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0010_auto_20151111_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='reactor_model',
        ),
    ]
