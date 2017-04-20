# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_auto_20170419_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(default=b'general', max_length=14, choices=[(b'general', b'General'), (b'vacation', b'Vacation'), (b'festival', b'Festival'), (b'camping', b'Camping'), (b'entertainment', b'Entertainment'), (b'show', b'Show')]),
        ),
    ]
