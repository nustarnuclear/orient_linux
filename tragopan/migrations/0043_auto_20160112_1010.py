# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0042_auto_20160111_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='burnablepoisonmaterial',
            name='radius',
            field=models.DecimalField(max_digits=7, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, help_text='unit:cm'),
        ),
        migrations.AlterField(
            model_name='fuelelementradialmap',
            name='fuel_element',
            field=models.ForeignKey(related_name='materials', to='tragopan.FuelElement'),
        ),
        migrations.AlterField(
            model_name='guidetube',
            name='fuel_assembly_model',
            field=models.OneToOneField(to='tragopan.FuelAssemblyModel', related_name='guide_tube'),
        ),
        migrations.AlterField(
            model_name='instrumenttube',
            name='fuel_assembly_model',
            field=models.OneToOneField(to='tragopan.FuelAssemblyModel', related_name='instrument_tube'),
        ),
    ]
