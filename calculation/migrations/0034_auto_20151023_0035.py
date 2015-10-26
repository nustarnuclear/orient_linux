# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0033_multipleloadingpattern_pre_loading_pattern'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='multipleloadingpattern',
            unique_together=set([('user', 'name')]),
        ),
    ]
