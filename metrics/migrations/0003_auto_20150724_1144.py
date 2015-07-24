# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0002_auto_20150724_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservideometric',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
