# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0067_auto_20160125_1443'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='burnablepoisonrodmap',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='burnablepoisonrodmap',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='burnablepoisonrodmap',
            name='burnable_poison_position',
        ),
        migrations.DeleteModel(
            name='BurnablePoisonRodMap',
        ),
    ]
