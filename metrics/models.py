import calendar
from datetime import timedelta
import random

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class MetricsQuerySet(models.QuerySet):
    def total_plays(self):
        return self.aggregate(play_count=Sum('play_count'))

    def total_seconds(self):
        return self.aggregate(seconds_played=Sum('seconds_played'))


class MetricsManager(models.Manager):
    def get_queryset(self):
        return MetricsQuerySet(self.model, using=self._db)

    def total_seconds_for_recording(self, recording_id):
        return self.get_queryset().filter(recording_id=recording_id).total_seconds()

    def total_plays_for_recording(self, recording_id):
        return self.get_queryset().filter(recording_id=recording_id).total_plays()

    def total_seconds_for_artist(self, artist_recording_ids):
        return self.get_queryset().filter(recording_id__in=artist_recording_ids).total_seconds()

    def total_plays_for_artist(self, artist_recording_ids):
        return self.get_queryset().filter(recording_id__in=artist_recording_ids).total_plays()

    def total_plays(self):
        return self.get_queryset().total_plays()

    def total_seconds(self):
        return self.get_queryset().total_seconds()

    def total_plays_for_month(self, month, year):
        return self.get_queryset().filter(date__month=month, date__year=year).total_plays()

    def total_seconds_for_month(self, month, year):
        return self.get_queryset().filter(date__month=month, date__year=year).total_seconds()

    def date_plays_for_recording(self, recording_id, month, year):
        values = self.get_queryset().filter(
            recording_id=recording_id, date__month=month, date__year=year).values_list('date', 'play_count').order_by('date')
        days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        day_values = {date.day: count for date, count in values}
        values_list = [day_values.get(day_number, 0) for day_number in days]
        return values_list

    def date_seconds_for_recording(self, recording_id, month, year):
        values = self.get_queryset().filter(
            recording_id=recording_id, date__month=month, date__year=year).values_list('date', 'seconds_played').order_by('date')
        days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        day_values = {date.day: count for date, count in values}
        values_list = [day_values.get(day_number, 0) for day_number in days]
        return values_list

    def full_stats_for_recording(self, recording_id):
        return self.get_queryset().filter(recording_id=recording_id).total_plays()

    def create_random(self):
        today = timezone.now().date()
        params = {}
        params['date'] = today - timedelta(days=random.randrange(1, 90))
        params['recording_id'] = random.randrange(1, 10)
        params['user_id'] = random.randrange(1, 10)
        params['seconds_played'] = random.randrange(10, 600, 10)
        self.create(**params)

    def create_random_for_user(self, user_id):
        today = timezone.now()
        params = {}
        params['user_id'] = user_id
        for day in range(1, 90):
            params['date'] = (today - timedelta(days=day)).date()
            for recording_id in range(1, 5):
                params['recording_id'] = recording_id
                params['seconds_played'] = random.randrange(10, 600, 10)
                params['play_count'] = random.randrange(1, 100, 1)
                print params
                self.create(**params)


class UserVideoMetric(models.Model):
    recording_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(blank=False)
    date = models.DateField(blank=False, default=timezone.now)
    last_ping = models.DateTimeField(auto_now=True)
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=1)  # it gets created on the first play

    objects = MetricsManager()

    class Meta:
        unique_together = ('recording_id', 'user_id', 'date')

    def __str__(self):
        return "V{0} U{1} D{2.year}/{2.month}/{2.day} C{3}".format(
            self.recording_id, self.user_id, self.date, self.seconds_played)
