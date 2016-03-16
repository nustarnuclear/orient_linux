# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0118_auto_20160316_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelassemblytype',
            name='assembly_enrichment',
            field=models.DecimalField(max_digits=9, blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], decimal_places=6, help_text='meaningful only if using the one unique enrichment fuel'),
        ),
    ]
