# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0029_auto_20151229_1017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='prerobin_identifier',
        ),
        migrations.AlterField(
            model_name='basicmaterial',
            name='name',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='nameCH',
            field=models.CharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='nameEN',
            field=models.CharField(max_length=40, blank=True),
        ),
    ]
