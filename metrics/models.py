import calendar
from django.db import models
from django.db.models import Sum


class MetricsQuerySet(models.QuerySet):
    def total_plays(self):
        return self.aggregate(play_count=Sum('play_count'))

    def total_seconds(self):
        return self.aggregate(seconds_played=Sum('seconds_played'))


class MetricsManager(models.Manager):
    def get_queryset(self):
        return MetricsQuerySet(self.model, using=self._db)

    def total_seconds_for_media(self, media_id):
        return self.get_queryset().filter(media_id=media_id).total_seconds()

    def total_plays_for_media(self, media_id):
        return self.get_queryset().filter(media_id=media_id).total_plays()

    def total_seconds_for_user(self, user_id):
        return self.get_queryset().filter(user_id=user_id).total_seconds()

    def total_plays_for_user(self, user_id):
        return self.get_queryset().filter(user_id=user_id).total_plays()

    def total_plays(self):
        return self.get_queryset().total_plays()

    def total_seconds(self):
        return self.get_queryset().total_seconds()

    def total_plays_for_month(self, month, year):
        return self.get_queryset().filter(date__month=month, date__year=year).total_plays()

    def total_seconds_for_month(self, month, year):
        return self.get_queryset().filter(date__month=month, date__year=year).total_seconds()

    def date_plays_for_media(self, media_id, month, year):
        values = self.get_queryset().filter(
            media_id=media_id, date__month=month, date__year=year).values_list('date', 'play_count').order_by('date')
        days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        day_values = {date.day: count for date, count in values}
        values_list = [day_values.get(day_number, 0) for day_number in days]
        return values_list

    def date_seconds_for_media(self, media_id, month, year):
        values = self.get_queryset().filter(
            media_id=media_id, date__month=month, date__year=year).values_list('date', 'seconds_played').order_by('date')
        days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        day_values = {date.day: count for date, count in values}
        values_list = [day_values.get(day_number, 0) for day_number in days]
        return values_list

    def full_stats_for_media(self, media_id):
        return self.get_queryset().filter(media_id=media_id).total_plays()


class UserVideoMetric(models.Model):
    media_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(blank=False)
    date = models.DateField(blank=False, auto_now_add=True)
    last_ping = models.DateTimeField(auto_now=True)
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=1)  # it gets created on the first play

    objects = MetricsManager()

    class Meta:
        unique_together = ('media_id', 'user_id', 'date')

    def __str__(self):
        return "V{0} U{1} D{2.year}/{2.month}/{2.day} C{3}".format(
            self.media_id, self.user_id, self.date, self.seconds_played)
