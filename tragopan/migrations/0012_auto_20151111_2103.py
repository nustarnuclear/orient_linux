# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0011_remove_controlrodassembly_reactor_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodcluster',
            name='basez',
            field=models.DecimalField(null=True, help_text='unit:cm', decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], blank=True, max_digits=7),
        ),
        migrations.AddField(
            model_name='controlrodcluster',
            name='step_size',
            field=models.DecimalField(null=True, help_text='unit:cm', decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], blank=True, max_digits=7),
        ),
        migrations.AlterField(
            model_name='controlrodcluster',
            name='reactor_model',
            field=models.ForeignKey(to='tragopan.ReactorModel', related_name='control_rod_clusters'),
        ),
    ]
