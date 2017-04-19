# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0010_auto_20160105_1307'),
        ('events', '0010_event_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='gallery',
            field=models.OneToOneField(null=True, to='photologue.Gallery'),
        ),
    ]
