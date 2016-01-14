# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0057_auto_20160114_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlrodassemblytype',
            name='reactor_model',
            field=models.ForeignKey(related_name='cra_types', default=4, to='tragopan.ReactorModel'),
            preserve_default=False,
        ),
    ]
