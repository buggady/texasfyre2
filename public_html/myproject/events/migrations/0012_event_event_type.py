# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_event_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.TextField(null=True),
        ),
    ]
