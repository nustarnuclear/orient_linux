# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0142_auto_20160421_1425'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelassemblyloadingpattern',
            name='control_rod_assembly',
        ),
    ]
