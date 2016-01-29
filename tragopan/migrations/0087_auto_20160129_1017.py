# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0086_auto_20160128_1506'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fuelelementpelletloadingscheme',
            old_name='section',
            new_name='length',
        ),
        migrations.AddField(
            model_name='fuelelementpelletloadingscheme',
            name='section_num',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
