# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0051_remove_prerobintask_symmetry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assemblylamination',
            name='height',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', max_digits=10, verbose_name='bottom_height', decimal_places=5),
        ),
        migrations.AlterField(
            model_name='assemblylamination',
            name='pre_robon_input',
            field=models.ForeignKey(related_name='layers', to='calculation.PreRobinInput'),
        ),
    ]
