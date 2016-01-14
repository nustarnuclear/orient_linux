# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0054_auto_20160114_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='type',
        ),
    ]
