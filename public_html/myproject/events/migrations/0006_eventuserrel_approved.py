# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20170125_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventuserrel',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
