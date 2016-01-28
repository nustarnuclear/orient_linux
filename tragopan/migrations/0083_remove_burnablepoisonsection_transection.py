# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0082_burnablepoisonsection_material_transection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonsection',
            name='transection',
        ),
    ]
