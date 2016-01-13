# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0046_auto_20160112_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlrodradialmap',
            name='control_rod',
            field=models.ForeignKey(to='tragopan.ControlRodType', related_name='radial_materials'),
        ),
    ]
