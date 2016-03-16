# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0115_auto_20160315_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassemblytype',
            name='overall_length',
            field=models.DecimalField(max_digits=7, help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], default=400, decimal_places=3),
        ),
    ]
