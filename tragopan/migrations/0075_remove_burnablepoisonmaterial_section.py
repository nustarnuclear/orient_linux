# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0074_auto_20160127_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonmaterial',
            name='section',
        ),
    ]
