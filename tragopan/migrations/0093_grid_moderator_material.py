# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0092_auto_20160202_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='moderator_material',
            field=models.ForeignKey(to='tragopan.Material', default=70, related_name='grid_moderator'),
        ),
    ]
