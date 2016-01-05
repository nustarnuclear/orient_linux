# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0020_remove_ibis_ibis_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='egretinputxml',
            name='unit',
        ),
        migrations.DeleteModel(
            name='EgretInputXML',
        ),
    ]
