# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tragopan', '0112_auto_20151029_0259'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fuelassemblytype',
            old_name='fuel_element_Type_position',
            new_name='fuel_element_type_position',
        ),
        migrations.AlterOrderWithRespectTo(
            name='operationparameter',
            order_with_respect_to='cycle',
        ),
    ]
