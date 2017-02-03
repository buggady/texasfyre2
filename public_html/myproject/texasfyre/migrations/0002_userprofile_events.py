# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '__first__'),
        ('texasfyre', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='events',
            field=models.ForeignKey(blank=True, to='events.Event', null=True),
        ),
    ]
