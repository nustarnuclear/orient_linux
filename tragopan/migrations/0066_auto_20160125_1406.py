# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0065_auto_20160125_1352'),
    ]

    operations = [
        migrations.CreateModel(
            name='BurnablePoisonAssemblyMap',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('row', models.PositiveSmallIntegerField()),
                ('column', models.PositiveSmallIntegerField()),
                ('burnable_poison_assembly', models.ForeignKey(to='tragopan.BurnablePoisonAssembly')),
                ('burnable_poison_rod', models.ForeignKey(to='tragopan.BurnablePoisonRod')),
            ],
            options={
                'db_table': 'burnable_poison_assembly_map',
            },
        ),
        migrations.AddField(
            model_name='burnablepoisonassembly',
            name='map',
            field=models.ManyToManyField(to='tragopan.BurnablePoisonRod', through='tragopan.BurnablePoisonAssemblyMap'),
        ),
    ]
