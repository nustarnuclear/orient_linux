# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0076_burnablepoisonsection_transection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='burnablepoisonassembly',
            options={'verbose_name_plural': 'burnable poison assemblies'},
        ),
        migrations.AlterModelOptions(
            name='burnablepoisonrod',
            options={},
        ),
        migrations.AddField(
            model_name='burnablepoisonassembly',
            name='symmetry',
            field=models.BooleanField(help_text='satisfy 1/8 symmetry', default=True),
        ),
        migrations.AddField(
            model_name='controlrodassemblytype',
            name='symmetry',
            field=models.BooleanField(help_text='satisfy 1/8 symmetry', default=True),
        ),
        migrations.AddField(
            model_name='fuelassemblytype',
            name='symmetry',
            field=models.BooleanField(help_text='satisfy 1/8 symmetry', default=True),
        ),
        migrations.AlterField(
            model_name='burnablepoisonmaterial',
            name='transection',
            field=models.ForeignKey(blank=True, to='tragopan.BurnablePoisonTransection', related_name='radial_materials', null=True),
        ),
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='length',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text='unit:cm', max_digits=10, decimal_places=5, null=True),
        ),
    ]
