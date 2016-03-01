# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0096_remove_mixturecomposition_input_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialWeightComposition',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('percent', models.DecimalField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], max_digits=9, decimal_places=6, help_text='unit:%')),
                ('basic_material', models.ForeignKey(to='tragopan.BasicMaterial')),
            ],
            options={
                'verbose_name_plural': 'Weight Composition',
                'verbose_name': 'Weight Composition',
                'db_table': 'material_weight_composition',
            },
        ),
        migrations.AlterModelOptions(
            name='mixturecomposition',
            options={'verbose_name_plural': 'Volume Composition', 'verbose_name': 'Volume Composition'},
        ),
        migrations.AlterField(
            model_name='material',
            name='basic_material',
            field=models.OneToOneField(to='tragopan.BasicMaterial', null=True, blank=True, related_name='materials'),
        ),
        migrations.AddField(
            model_name='materialweightcomposition',
            name='mixture',
            field=models.ForeignKey(related_name='weight_mixtures', to='tragopan.Material'),
        ),
        migrations.AddField(
            model_name='material',
            name='weight_composition',
            field=models.ManyToManyField(to='tragopan.BasicMaterial', through='tragopan.MaterialWeightComposition'),
        ),
    ]
