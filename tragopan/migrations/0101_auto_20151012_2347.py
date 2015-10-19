# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0100_auto_20150921_1143'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'verbose_name_plural': 'Material repository', 'managed': False, 'verbose_name': 'Material repository'},
        ),
        migrations.AlterModelOptions(
            name='nuclide',
            options={'managed': False, 'ordering': ['element']},
        ),
        migrations.AlterUniqueTogether(
            name='burnablepoisonassemblyloadingpattern',
            unique_together=set([]),
        ),
    ]
