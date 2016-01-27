# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0068_auto_20160125_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='BurnablePoisonSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('section_num', models.PositiveSmallIntegerField()),
                ('burnable_poison_rod', models.ForeignKey(to='tragopan.BurnablePoisonRod')),
                ('radial_map', models.ManyToManyField(through='tragopan.BurnablePoisonMaterial', to='tragopan.Material')),
            ],
            options={
                'db_table': 'burnable_poison_section',
            },
        ),
        migrations.AddField(
            model_name='burnablepoisonmaterial',
            name='section',
            field=models.ForeignKey(blank=True, null=True, to='tragopan.BurnablePoisonSection'),
        ),
    ]
