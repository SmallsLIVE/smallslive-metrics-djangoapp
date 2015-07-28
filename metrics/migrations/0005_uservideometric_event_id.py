# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0004_uservideometric_recording_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideometric',
            name='event_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
