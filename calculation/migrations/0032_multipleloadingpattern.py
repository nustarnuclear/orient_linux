# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import calculation.models


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0111_controlrodassembly_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calculation', '0031_auto_20151020_0314'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultipleLoadingPattern',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('name', models.CharField(max_length=32)),
                ('xml_file', models.FileField(upload_to=calculation.models.get_custom_loading_pattern)),
                ('cycle', models.ForeignKey(to='tragopan.Cycle')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'multiple_loading_pattern',
            },
        ),
    ]
