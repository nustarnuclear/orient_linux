# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0128_auto_20160331_1401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='burnablepoisonassemblyloadingpattern',
            name='burnable_poison_assembly',
        ),
        migrations.RemoveField(
            model_name='burnablepoisonassemblyloadingpattern',
            name='cycle',
        ),
        migrations.RemoveField(
            model_name='burnablepoisonassemblyloadingpattern',
            name='reactor_position',
        ),
        migrations.AlterField(
            model_name='fuelassemblyloadingpattern',
            name='cycle',
            field=models.ForeignKey(related_name='loading_patterns', to='tragopan.Cycle'),
        ),
        migrations.DeleteModel(
            name='BurnablePoisonAssemblyLoadingPattern',
        ),
    ]
