# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0103_auto_20151017_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='burnablepoisonassemblyloadingpattern',
            name='cycle',
            field=models.ForeignKey(related_name='bpa_loading_patterns', to='tragopan.Cycle'),
        ),
    ]
