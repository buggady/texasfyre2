# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_home_town'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='theme_color',
            field=models.CharField(default=b'blue', max_length=10),
        ),
    ]
