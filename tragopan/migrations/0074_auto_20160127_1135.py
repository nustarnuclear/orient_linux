# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0073_remove_burnablepoisonsection_radial_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='BurnablePoisonTransection',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('radius', models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm', decimal_places=5)),
                ('radial_map', models.ManyToManyField(through='tragopan.BurnablePoisonMaterial', to='tragopan.Material')),
            ],
            options={
                'db_table': 'burnable_poison_transection',
            },
        ),
        migrations.AddField(
            model_name='burnablepoisonmaterial',
            name='transection',
            field=models.ForeignKey(to='tragopan.BurnablePoisonTransection', null=True, blank=True),
        ),
    ]
