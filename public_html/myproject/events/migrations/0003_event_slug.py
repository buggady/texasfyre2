# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20170114_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=datetime.datetime(2017, 1, 25, 1, 24, 16, 263727, tzinfo=utc), populate_from=b'title', editable=False),
            preserve_default=False,
        ),
    ]
