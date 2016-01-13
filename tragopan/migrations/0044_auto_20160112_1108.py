# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0043_auto_20160112_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicmaterial',
            name='name',
            field=models.CharField(unique=True, max_length=16),
        ),
    ]
