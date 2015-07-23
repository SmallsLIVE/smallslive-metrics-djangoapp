# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserVideoMetric',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('media_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('date', models.DateField()),
                ('last_ping', models.DateTimeField(auto_now=True)),
                ('seconds_played', models.IntegerField(default=0)),
                ('play_count', models.IntegerField(default=0)),
            ],
        ),
    ]
