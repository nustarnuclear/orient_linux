# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0075_remove_burnablepoisonmaterial_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='burnablepoisonsection',
            name='transection',
            field=models.ForeignKey(default=1, to='tragopan.BurnablePoisonTransection'),
            preserve_default=False,
        ),
    ]
