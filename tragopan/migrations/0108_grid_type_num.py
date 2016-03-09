# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0107_remove_grid_moderator_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='type_num',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
