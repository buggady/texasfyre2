# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20170419_1904'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_type',
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(default=b'general', max_length=10, choices=[(b'general', b'General'), (b'vacation', b'Vacation'), (b'festival', b'Festival'), (b'show', b'Show')]),
        ),
    ]
