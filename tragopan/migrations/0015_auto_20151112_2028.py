# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0014_auto_20151112_2025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cycle',
            options={'verbose_name': 'Operation cycle', 'ordering': ['unit', 'cycle']},
        ),
    ]
