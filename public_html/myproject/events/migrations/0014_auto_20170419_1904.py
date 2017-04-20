# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20170419_1902'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_type',
            new_name='event_focus',
        ),
    ]
