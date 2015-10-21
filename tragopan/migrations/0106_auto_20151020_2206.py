# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0105_auto_20151020_2157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='controlrodassembly',
            old_name='reator_model',
            new_name='reactor_model',
        ),
    ]
