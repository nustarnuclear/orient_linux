# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0032_multipleloadingpattern'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipleloadingpattern',
            name='pre_loading_pattern',
            field=models.ForeignKey(null=True, to='calculation.MultipleLoadingPattern', blank=True, related_name='post_loading_patterns'),
        ),
    ]
