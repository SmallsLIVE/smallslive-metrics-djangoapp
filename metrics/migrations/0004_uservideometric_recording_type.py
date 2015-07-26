# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0003_auto_20150724_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideometric',
            name='recording_type',
            field=models.CharField(default='V', max_length=1, choices=[(b'A', b'Audio'), (b'V', b'Video')]),
            preserve_default=False,
        ),
    ]
