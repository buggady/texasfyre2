# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventuserrel',
            name='amount_paid',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
    ]
