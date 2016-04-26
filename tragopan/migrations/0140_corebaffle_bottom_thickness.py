# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0139_auto_20160418_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='corebaffle',
            name='bottom_thickness',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], max_digits=7, decimal_places=3, help_text='unit:cm', default=7),
        ),
    ]
