# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0090_remove_controlrodtype_radial_map'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlrodradialmap',
            name='control_rod',
        ),
        migrations.RemoveField(
            model_name='controlrodradialmap',
            name='material',
        ),
        migrations.RemoveField(
            model_name='controlrodassemblytype',
            name='side_pin_num',
        ),
        migrations.AddField(
            model_name='controlrodtype',
            name='black',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='controlrodsection',
            name='material_transection',
            field=models.ForeignKey(to='tragopan.MaterialTransection', related_name='control_rod_sections'),
        ),
        migrations.DeleteModel(
            name='ControlRodRadialMap',
        ),
    ]
