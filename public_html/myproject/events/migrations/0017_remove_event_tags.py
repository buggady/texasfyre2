# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20170419_1906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='tags',
        ),
    ]
