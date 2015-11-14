# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0017_auto_20151113_1455'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='operationparameter',
            order_with_respect_to=None,
        ),
        migrations.RemoveField(
            model_name='operationparameter',
            name='cycle',
        ),
    ]
