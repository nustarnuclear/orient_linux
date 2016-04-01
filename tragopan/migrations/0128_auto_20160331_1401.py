# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0127_auto_20160328_1450'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grid',
            name='spring_material',
        ),
        migrations.RemoveField(
            model_name='grid',
            name='type_num',
        ),
    ]
