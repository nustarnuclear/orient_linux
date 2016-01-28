# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0081_auto_20160128_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='burnablepoisonsection',
            name='material_transection',
            field=models.ForeignKey(default=1, to='tragopan.MaterialTransection'),
            preserve_default=False,
        ),
    ]
