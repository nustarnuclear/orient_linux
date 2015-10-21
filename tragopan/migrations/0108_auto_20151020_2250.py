# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0107_auto_20151020_2228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodassembly',
            name='fuel_assembly_model',
        ),
        migrations.AddField(
            model_name='controlrodassembly',
            name='basez',
            field=models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], decimal_places=3, max_digits=7, default=18),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlrodassembly',
            name='step_size',
            field=models.DecimalField(help_text='unit:cm', validators=[django.core.validators.MinValueValidator(0)], decimal_places=3, max_digits=7, default=1),
            preserve_default=False,
        ),
    ]
