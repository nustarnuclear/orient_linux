# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0159_fuelassemblyloadingpattern_rotation_degree'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='controlrodassemblytype',
            options={'verbose_name': 'Control rod assembly', 'verbose_name_plural': 'Control rod assemblies'},
        ),
        migrations.AlterModelOptions(
            name='operationdistributiondata',
            options={'verbose_name_plural': 'operation_distribution_data'},
        ),
        migrations.AlterModelOptions(
            name='wimsnuclidedata',
            options={'verbose_name_plural': 'wims nuclide data'},
        ),
        migrations.AlterModelOptions(
            name='wmiselementdata',
            options={'verbose_name_plural': 'wmis element data'},
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='HFP_cool_inlet_temp',
            field=models.DecimalField(help_text='unit:K', blank=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=15, null=True, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='HZP_cool_inlet_temp',
            field=models.DecimalField(help_text='unit:K', blank=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=15, null=True, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='unitparameter',
            name='cold_state_cool_temp',
            field=models.DecimalField(help_text='unit:K', blank=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=15, null=True, decimal_places=5),
        ),
    ]
