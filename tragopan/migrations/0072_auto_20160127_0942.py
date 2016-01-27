# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0071_auto_20160126_1243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='burnablepoisonsection',
            options={'ordering': ['section_num']},
        ),
        migrations.AddField(
            model_name='burnablepoisonrod',
            name='bottom_height',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, default=7.4575, max_digits=7, help_text='unit:cm based on the bottom of fuel active part'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='burnablepoisonmaterial',
            name='section',
            field=models.ForeignKey(related_name='radial_materials', to='tragopan.BurnablePoisonSection'),
        ),
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='active_length',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, max_digits=10, help_text='unit:cm'),
        ),
        migrations.AlterField(
            model_name='burnablepoisonrod',
            name='length',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(0)], decimal_places=5, max_digits=10, help_text='unit:cm'),
        ),
        migrations.AlterField(
            model_name='burnablepoisonsection',
            name='burnable_poison_rod',
            field=models.ForeignKey(related_name='sections', to='tragopan.BurnablePoisonRod'),
        ),
    ]
