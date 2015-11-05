# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import calculation.models
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseFuel',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('fuel_identity', models.CharField(max_length=32)),
                ('base_bottom', models.DecimalField(default=0, max_digits=10, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='cm')),
                ('offset', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'base_fuel',
            },
        ),
        migrations.CreateModel(
            name='BaseFuelComposition',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('height', models.DecimalField(max_digits=10, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='cm')),
                ('base_fuel', models.ForeignKey(to='calculation.BaseFuel', related_name='composition')),
            ],
            options={
                'db_table': 'base_fuel_composition',
            },
        ),
        migrations.CreateModel(
            name='EgretInputXML',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('base_component_path', models.FilePathField(match='.*base_component\\.xml$', max_length=200, null=True, blank=True, recursive=True, path='/home/django/.django_project/media')),
                ('base_core_path', models.FilePathField(match='.*base_core\\.xml$', max_length=200, null=True, blank=True, recursive=True, path='/home/django/.django_project/media')),
                ('loading_pattern_path', models.FilePathField(match='.*loading_pattern\\.xml$', max_length=200, null=True, blank=True, recursive=True, path='/home/django/.django_project/media')),
                ('unit', models.ForeignKey(to='tragopan.UnitParameter')),
            ],
            options={
                'db_table': 'egret_input_xml',
            },
        ),
        migrations.CreateModel(
            name='EgretTask',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('task_name', models.CharField(max_length=32)),
                ('task_type', models.CharField(max_length=32)),
                ('result_path', models.FilePathField(match='.*\\.xml$', max_length=200, null=True, blank=True, recursive=True, path='/home/django/.django_project/media')),
                ('egret_input_file', models.FileField(blank=True, null=True, upload_to=calculation.models.get_egret_upload_path)),
                ('follow_index', models.BooleanField()),
                ('task_status', models.PositiveSmallIntegerField(default=0, choices=[(0, 'not yet'), (1, 'finished')])),
                ('restart_file', models.FilePathField(blank=True, max_length=200, recursive=True, null=True, path='/home/django/.django_project/media')),
            ],
            options={
                'db_table': 'egret_task',
            },
        ),
        migrations.CreateModel(
            name='Ibis',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('ibis_name', models.CharField(max_length=32)),
                ('active_length', models.DecimalField(default=365.8, max_digits=10, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='unit:cm')),
                ('ibis_file', models.FileField(upload_to=calculation.models.get_ibis_upload_path)),
                ('burnable_poison_assembly', models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True)),
                ('fuel_assembly_type', models.ForeignKey(to='tragopan.FuelAssemblyType')),
                ('plant', models.ForeignKey(to='tragopan.Plant')),
                ('reactor_model', models.ForeignKey(to='tragopan.ReactorModel')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'db_table': 'ibis',
                'verbose_name_plural': 'Ibis',
            },
        ),
        migrations.CreateModel(
            name='MultipleLoadingPattern',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('name', models.CharField(max_length=32)),
                ('xml_file', models.FileField(upload_to=calculation.models.get_custom_loading_pattern)),
                ('cycle', models.ForeignKey(to='tragopan.Cycle')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('pre_loading_pattern', models.ForeignKey(to='calculation.MultipleLoadingPattern', null=True, blank=True, related_name='post_loading_patterns')),
                ('from_database', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'multiple_loading_pattern',
            },
        ),
        migrations.CreateModel(
            name='PreRobinBranch',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('identity', models.CharField(max_length=32)),
                ('max_boron_density', models.PositiveSmallIntegerField(blank=True, null=True, help_text='ppm')),
                ('min_boron_density', models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='ppm')),
                ('boron_density_interval', models.PositiveSmallIntegerField(default=200, blank=True, null=True, help_text='ppm')),
                ('max_fuel_temperature', models.PositiveSmallIntegerField(blank=True, null=True, help_text='K')),
                ('min_fuel_temperature', models.PositiveSmallIntegerField(blank=True, null=True, help_text='K')),
                ('fuel_temperature_interval', models.PositiveSmallIntegerField(default=50, blank=True, null=True, help_text='K')),
                ('max_moderator_temperature', models.PositiveSmallIntegerField(blank=True, null=True, help_text='K')),
                ('min_moderator_temperature', models.PositiveSmallIntegerField(blank=True, null=True, help_text='K')),
                ('moderator_temperature_interval', models.PositiveSmallIntegerField(default=4, blank=True, null=True, help_text='K')),
                ('shutdown_cooling_days', models.PositiveSmallIntegerField(blank=True, null=True, help_text='day')),
                ('xenon', models.BooleanField(default=False, verbose_name='set xenon density to 0?')),
                ('control_rod_assembly', models.ForeignKey(to='tragopan.ControlRodAssembly', null=True, blank=True)),
            ],
            options={
                'db_table': 'pre_robin_branch',
                'verbose_name_plural': 'branches',
            },
        ),
        migrations.CreateModel(
            name='PreRobinInput',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('segment_identity', models.CharField(max_length=32)),
                ('file_type', models.CharField(max_length=9, choices=[('BASE_FUEL', 'BASE_FUEL'), ('BP_OUT', 'BP_OUT'), ('BR', 'BR')])),
                ('power_density', models.DecimalField(decimal_places=5, null=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=10, blank=True, help_text='w/g')),
                ('assembly_maxium_burnup', models.DecimalField(decimal_places=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], max_digits=7, blank=True, help_text='GWd/tU')),
                ('boron_density', models.DecimalField(decimal_places=5, null=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=10, blank=True, help_text='ppm')),
                ('moderator_temperature', models.DecimalField(decimal_places=5, null=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=10, blank=True, help_text='K')),
                ('fuel_temperature', models.DecimalField(decimal_places=5, null=True, validators=[django.core.validators.MinValueValidator(0)], max_digits=10, blank=True, help_text='K')),
                ('num_fuel_assembly', models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3)], null=True)),
                ('num_edit_node', models.PositiveSmallIntegerField(default=16, blank=True, choices=[(16, 16), (4, 4)], null=True)),
                ('pre_robin_file', models.FileField(blank=True, null=True, upload_to=calculation.models.get_pre_robin_upload_path)),
                ('branch_composition', models.ManyToManyField(to='calculation.PreRobinBranch', related_name='branches')),
                ('burnable_poison_assembly', models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True)),
                ('core_baffle', models.ForeignKey(to='tragopan.CoreBaffle', null=True, blank=True)),
                ('fuel_assembly_type', models.ForeignKey(to='tragopan.FuelAssemblyType')),
                ('grid', models.ForeignKey(to='tragopan.Grid', null=True, blank=True)),
                ('plant', models.ForeignKey(to='tragopan.Plant')),
            ],
            options={
                'db_table': 'pre_robin_input',
            },
        ),
        migrations.CreateModel(
            name='PreRobinModel',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('model_name', models.CharField(max_length=32)),
                ('system_pressure', models.DecimalField(default=15.51, max_digits=7, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='MPa')),
                ('dep_strategy', models.CharField(default='LLR', blank=True, max_length=3, choices=[('LLR', 'LLR'), ('PPC', 'PPC'), ('LR', 'LR'), ('PC', 'PC')], null=True)),
                ('track_density', models.DecimalField(default=0.03, max_digits=5, decimal_places=5, validators=[django.core.validators.MinValueValidator(0)], help_text='cm')),
                ('polar_type', models.CharField(default='LCMD', max_length=4, choices=[('LCMD', 'LCMD'), ('TYPL', 'TYPL'), ('DeCT', 'DeCT')])),
                ('polar_azimuth', models.CommaSeparatedIntegerField(default='4,16', max_length=50)),
                ('iter_inner', models.PositiveSmallIntegerField(default=3)),
                ('iter_outer', models.PositiveSmallIntegerField(default=100)),
                ('eps_keff', models.DecimalField(default=1e-05, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5)),
                ('eps_flux', models.DecimalField(default=0.0001, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], decimal_places=5)),
                ('leakage_corrector_path', models.PositiveSmallIntegerField(default=2, choices=[(0, 0), (1, 1), (2, 2)])),
                ('leakage_corrector_method', models.CharField(default='B1', max_length=2, choices=[('B1', 'B1'), ('P1', 'P1')])),
                ('buckling_or_keff', models.DecimalField(default=1, max_digits=10, decimal_places=5)),
                ('condensation_path', models.PositiveSmallIntegerField(default=1, choices=[(0, 0), (1, 1), (2, 2)])),
                ('num_group_2D', models.PositiveSmallIntegerField(default=25, choices=[(2, 2), (3, 3), (4, 4), (8, 8), (18, 18), (25, 25), (33, 33)])),
                ('num_group_edit', models.PositiveSmallIntegerField(default=2, choices=[(2, 2), (3, 3), (4, 4), (8, 8), (18, 18), (25, 25), (33, 33)])),
                ('micro_xs_output', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'db_table': 'pre_robin_model',
            },
        ),
        migrations.CreateModel(
            name='RobinFile',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('time_inserted', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True)),
                ('file_type', models.CharField(max_length=9, choices=[('BASE_FUEL', 'BASE_FUEL'), ('BP_OUT', 'BP_OUT'), ('BR', 'BR')])),
                ('input_file', models.FileField(upload_to=calculation.models.get_robin_upload_path)),
                ('out1_file', models.FileField(upload_to=calculation.models.get_robin_upload_path)),
                ('log_file', models.FileField(upload_to=calculation.models.get_robin_upload_path)),
                ('burnable_poison_assembly', models.ForeignKey(to='tragopan.BurnablePoisonAssembly', null=True, blank=True)),
                ('fuel_assembly_type', models.ForeignKey(to='tragopan.FuelAssemblyType')),
                ('plant', models.ForeignKey(to='tragopan.Plant')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'db_table': 'robin_file',
            },
        ),
        migrations.AddField(
            model_name='prerobininput',
            name='pre_robin_model',
            field=models.ForeignKey(default=1, to='calculation.PreRobinModel'),
        ),
        migrations.AddField(
            model_name='prerobininput',
            name='use_pre_segment',
            field=models.ForeignKey(to='calculation.PreRobinInput', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='prerobininput',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='egrettask',
            name='loading_pattern',
            field=models.ForeignKey(to='calculation.MultipleLoadingPattern', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='egrettask',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='basefuelcomposition',
            name='ibis',
            field=models.ForeignKey(to='calculation.Ibis', related_name='base_fuel_compositions'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='axial_composition',
            field=models.ManyToManyField(to='calculation.Ibis', through='calculation.BaseFuelComposition', related_name='base_fuels'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='plant',
            field=models.ForeignKey(to='tragopan.Plant'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_four',
            field=models.ForeignKey(to='calculation.BaseFuel', null=True, blank=True, related_name='four'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_one',
            field=models.ForeignKey(to='calculation.BaseFuel', null=True, blank=True, related_name='one'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_three',
            field=models.ForeignKey(to='calculation.BaseFuel', null=True, blank=True, related_name='three'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_two',
            field=models.ForeignKey(to='calculation.BaseFuel', null=True, blank=True, related_name='two'),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AlterOrderWithRespectTo(
            name='robinfile',
            order_with_respect_to='fuel_assembly_type',
        ),
        migrations.AlterUniqueTogether(
            name='multipleloadingpattern',
            unique_together=set([('user', 'name')]),
        ),
        migrations.AlterOrderWithRespectTo(
            name='ibis',
            order_with_respect_to='reactor_model',
        ),
    ]
