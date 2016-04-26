# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0069_auto_20160415_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corebafflecalculation',
            name='pre_robin_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='calculation.PreRobinModel'),
        ),
        migrations.AlterField(
            model_name='corebafflecalculation',
            name='pre_robin_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='calculation.PreRobinTask'),
        ),
        migrations.AlterField(
            model_name='prerobinmodel',
            name='eps_flux',
            field=models.DecimalField(decimal_places=7, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], default=0.0001),
        ),
        migrations.AlterField(
            model_name='prerobinmodel',
            name='eps_keff',
            field=models.DecimalField(decimal_places=7, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], default=1e-05),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='core_baffle_calc',
            field=models.ForeignKey(blank=True, null=True, related_name='robin_tasks', to='calculation.CoreBaffleCalculation'),
        ),
    ]
