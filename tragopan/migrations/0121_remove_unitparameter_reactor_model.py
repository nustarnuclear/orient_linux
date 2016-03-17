# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0120_plant_reactor_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitparameter',
            name='reactor_model',
        ),
    ]
