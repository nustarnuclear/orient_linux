# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0106_auto_20160307_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grid',
            name='moderator_material',
        ),
    ]
