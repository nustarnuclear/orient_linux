# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0102_auto_20151017_0157'),
        ('calculation', '0025_auto_20151013_0059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basefuel',
            name='offset',
        ),
        migrations.AddField(
            model_name='basefuel',
            name='plant',
            field=models.ForeignKey(to='tragopan.Plant', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_four',
            field=models.ForeignKey(blank=True, related_name='four', to='calculation.BaseFuel', null=True),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_one',
            field=models.ForeignKey(blank=True, related_name='one', to='calculation.BaseFuel', null=True),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_three',
            field=models.ForeignKey(blank=True, related_name='three', to='calculation.BaseFuel', null=True),
        ),
        migrations.AddField(
            model_name='basefuel',
            name='quadrant_two',
            field=models.ForeignKey(blank=True, related_name='two', to='calculation.BaseFuel', null=True),
        ),
    ]
