# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0022_auto_20150928_2338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egrettask',
            name='result_xml',
        ),
    ]
