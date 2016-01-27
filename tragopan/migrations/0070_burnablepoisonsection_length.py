# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0069_auto_20160126_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='burnablepoisonsection',
            name='length',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=3, help_text='unit:cm', default=1),
            preserve_default=False,
        ),
    ]
