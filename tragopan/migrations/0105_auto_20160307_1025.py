# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0104_auto_20160307_1022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grid',
            name='inner_sleeve_thickness',
        ),
        migrations.RemoveField(
            model_name='grid',
            name='outer_sleeve_thickness',
        ),
        migrations.RemoveField(
            model_name='grid',
            name='spring_thickness',
        ),
    ]
