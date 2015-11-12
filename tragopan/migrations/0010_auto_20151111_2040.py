# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0009_auto_20151111_2036'),
    ]

    operations = [
        migrations.RenameField(
            model_name='controlrodassemblystep',
            old_name='control_rod_assembly',
            new_name='control_rod_cluster',
        ),
    ]
