# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0032_prerobinmodel_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssemblyLamination',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('height', models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', decimal_places=5, max_digits=10)),
                ('pre_robin_task', models.ForeignKey(to='calculation.PreRobinTask')),
                ('pre_robon_input', models.ForeignKey(to='calculation.PreRobinInput')),
            ],
            options={
                'db_table': 'assembly_lamination',
            },
        ),
        migrations.AlterField(
            model_name='prerobinmodel',
            name='default',
            field=models.BooleanField(help_text='set it as default', unique=True, default=False),
        ),
        migrations.AddField(
            model_name='prerobininput',
            name='task',
            field=models.ManyToManyField(through='calculation.AssemblyLamination', to='calculation.PreRobinTask'),
        ),
    ]
