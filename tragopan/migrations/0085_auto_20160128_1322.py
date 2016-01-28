# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0084_auto_20160128_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonmaterial',
            name='material',
        ),
        migrations.RemoveField(
            model_name='burnablepoisonmaterial',
            name='transection',
        ),
        migrations.RemoveField(
            model_name='burnablepoisontransection',
            name='radial_map',
        ),
        migrations.DeleteModel(
            name='BurnablePoisonMaterial',
        ),
        migrations.DeleteModel(
            name='BurnablePoisonTransection',
        ),
    ]
