# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0095_auto_20160224_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mixturecomposition',
            name='input_method',
        ),
    ]
