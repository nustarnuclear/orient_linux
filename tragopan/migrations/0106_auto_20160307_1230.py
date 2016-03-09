# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0105_auto_20160307_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='materialattribute',
            name='material',
        ),
        migrations.DeleteModel(
            name='MaterialAttribute',
        ),
    ]
