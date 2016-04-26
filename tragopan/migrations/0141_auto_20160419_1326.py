# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0140_corebaffle_bottom_thickness'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialVolumeComposition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('percent', models.DecimalField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], max_digits=8, help_text='unit:%', decimal_places=5)),
                ('material', models.ForeignKey(to='tragopan.Material')),
                ('mixture', models.ForeignKey(related_name='volume_mixtures', to='tragopan.Material')),
            ],
            options={
                'verbose_name': 'Volume Composition',
                'verbose_name_plural': 'Volume Composition',
                'db_table': 'material_volume_composition',
            },
        ),
        migrations.AddField(
            model_name='material',
            name='volume_composition',
            field=models.ManyToManyField(to='tragopan.Material', through='tragopan.MaterialVolumeComposition'),
        ),
    ]
