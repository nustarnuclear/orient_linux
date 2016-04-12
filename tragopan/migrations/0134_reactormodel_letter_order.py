# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0133_auto_20160408_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='letter_order',
            field=models.CharField(max_length=32, default='A B C D E F G H J K L M N'),
        ),
    ]
