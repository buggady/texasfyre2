# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texasfyre', '0002_userprofile_events'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='events',
        ),
    ]
