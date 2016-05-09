# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0146_auto_20160422_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='spring_material',
            field=models.ForeignKey(blank=True, null=True, to='tragopan.Material', related_query_name='grid_spring', related_name='grid_springs'),
        ),
    ]
