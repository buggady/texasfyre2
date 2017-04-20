# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20170419_1904'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_focus',
            new_name='event_type',
        ),
    ]
