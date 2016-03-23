# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0124_auto_20160321_1414'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reactormodel',
            name='boron_density',
        ),
    ]
