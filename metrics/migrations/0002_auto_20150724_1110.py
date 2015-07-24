# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uservideometric',
            old_name='media_id',
            new_name='recording_id',
        ),
        migrations.AlterField(
            model_name='uservideometric',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='uservideometric',
            name='play_count',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='uservideometric',
            unique_together=set([('recording_id', 'user_id', 'date')]),
        ),
    ]
