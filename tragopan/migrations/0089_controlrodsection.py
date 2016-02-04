# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0088_auto_20160129_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlRodSection',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('section_num', models.PositiveSmallIntegerField()),
                ('length', models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', decimal_places=3)),
                ('control_rod_type', models.ForeignKey(related_name='sections', to='tragopan.ControlRodType')),
                ('material_transection', models.ForeignKey(to='tragopan.MaterialTransection')),
            ],
            options={
                'db_table': 'control_rod_section',
                'ordering': ['section_num'],
            },
        ),
    ]
