# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0078_remove_server_queue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='egrettask',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='calculation.Server', blank=True),
        ),
        migrations.AlterField(
            model_name='egrettask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='multipleloadingpattern',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='prerobininput',
            name='burnup_point',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=4, default=65, max_digits=7, help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100'),
        ),
        migrations.AlterField(
            model_name='prerobininput',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='prerobintask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='robintask',
            name='server',
            field=models.ForeignKey(related_name='robin_tasks', on_delete=django.db.models.deletion.SET_NULL, null=True, to='calculation.Server', blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='name',
            field=models.CharField(unique=True, max_length=32, help_text='queue name for control'),
        ),
    ]
