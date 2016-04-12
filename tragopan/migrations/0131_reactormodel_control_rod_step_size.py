# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0130_auto_20160406_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactormodel',
            name='control_rod_step_size',
            field=models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], max_digits=7, default=1.5831, decimal_places=5),
        ),
    ]
