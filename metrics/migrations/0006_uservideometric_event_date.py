# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0005_uservideometric_event_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideometric',
            name='event_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
