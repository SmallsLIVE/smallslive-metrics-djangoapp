import calendar
import datetime
import itertools
import random

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from .utils import format_timespan


class MetricsQuerySet(models.QuerySet):
    def total_counts(self):
        counts = self.aggregate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))
        counts['seconds_played'] = counts['seconds_played'] or 0
        counts['play_count'] = counts['play_count'] or 0
        return counts

    def total_counts_annotate(self):
        return self.annotate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))


class MetricsManager(models.Manager):
    def get_queryset(self):
        return MetricsQuerySet(self.model, using=self._db)

    def counts_for_recording(self, recording_id, humanize=False):
        counts = self.get_queryset().filter(recording_id=recording_id).total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return counts

    def counts_for_artist(self, artist_recording_ids, humanize=False):
        counts = self.get_queryset().filter(recording_id__in=artist_recording_ids).total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return counts

    def _calculate_percentage(self, event_stat, total_stat):
        if total_stat > 0:
            percentage = float(event_stat) / float(total_stat)
        else:
            percentage = None
        return percentage

    def counts_for_event(self, event_id, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        this_week_counts = self.get_queryset().filter(
            date__range=(week_start, week_end), event_id=event_id).total_counts()
        this_month_counts = self.get_queryset().filter(
            date__month=now.month, date__year=now.year, event_id=event_id).total_counts()
        all_time_counts = self.get_queryset().filter(event_id=event_id).total_counts()

        total_archive_counts = self.total_archive_counts()
        this_week_counts['play_count_percentage'] = self._calculate_percentage(this_week_counts['play_count'],
                                                                               total_archive_counts['week'][
                                                                                   'play_count'])
        this_week_counts['seconds_played_percentage'] = self._calculate_percentage(this_week_counts['seconds_played'],
                                                                                   total_archive_counts['week'][
                                                                                       'seconds_played'])
        this_month_counts['play_count_percentage'] = self._calculate_percentage(this_month_counts['play_count'],
                                                                                total_archive_counts['month'][
                                                                                    'play_count'])
        this_month_counts['seconds_played_percentage'] = self._calculate_percentage(this_month_counts['seconds_played'],
                                                                                    total_archive_counts['month'][
                                                                                        'seconds_played'])
        all_time_counts['play_count_percentage'] = self._calculate_percentage(all_time_counts['play_count'],
                                                                              total_archive_counts['all_time'][
                                                                                  'play_count'])
        all_time_counts['seconds_played_percentage'] = self._calculate_percentage(all_time_counts['seconds_played'],
                                                                                  total_archive_counts['all_time'][
                                                                                      'seconds_played'])

        if humanize:
            this_week_counts['time_played'] = format_timespan(this_week_counts['seconds_played'])
            this_month_counts['time_played'] = format_timespan(this_month_counts['seconds_played'])
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])
        counts = {
            'week': this_week_counts,
            'month': this_month_counts,
            'all_time': all_time_counts
        }
        return counts

    def total_archive_counts(self, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        this_week_counts = self.get_queryset().filter(date__range=(week_start, week_end)).total_counts()
        this_month_counts = self.get_queryset().filter(date__month=now.month, date__year=now.year).total_counts()
        all_time_counts = self.get_queryset().total_counts()
        if humanize:
            this_week_counts['time_played'] = format_timespan(this_week_counts['seconds_played'])
            this_month_counts['time_played'] = format_timespan(this_month_counts['seconds_played'])
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])
        counts = {
            'week': this_week_counts,
            'month': this_month_counts,
            'all_time': all_time_counts
        }
        return counts

    def this_month_total_archive(self, humanize=False):
        now = timezone.now().date()
        counts = self.get_queryset().filter(date__month=now.month, date__year=now.year).total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return

    def this_week_counts(self, artist_event_ids=None, trends=False, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        qs = self.get_queryset().filter(date__range=(week_start, week_end))
        if artist_event_ids:
            counts = qs.filter(recording_id__in=artist_event_ids).total_counts()
            if trends:
                last_week_start = week_start - datetime.timedelta(weeks=1)
                last_week_end = week_end - datetime.timedelta(weeks=1)
                last_week_counts = self.get_queryset().filter(date__range=(last_week_start, last_week_end)).total_counts()
                this_week_seconds = int(counts['seconds_played'])
                last_week_seconds = int(last_week_counts['seconds_played'])
                if last_week_seconds != 0:
                    counts['seconds_played_trend'] = ((this_week_seconds - last_week_seconds) / last_week_seconds) * 100
                else:
                    counts['seconds_played_trend'] = 'n/a'

                this_week_plays = counts['play_count']
                last_week_plays = last_week_counts['play_count']
                if last_week_counts != 0:
                    counts['play_count_trend'] = ((this_week_plays - last_week_plays) / last_week_plays) * 100
                else:
                    counts['play_count_trend'] = 'n/a'
        else:
            counts = qs.total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return counts

    def monthly_counts(self, month, year, artist_event_ids=None, trends=False, humanize=False):
        qs = self.get_queryset().filter(date__month=month, date__year=year)
        if artist_event_ids:
            counts = qs.filter(event_id__in=artist_event_ids).total_counts()
            if trends:
                this_month = datetime.date(year, month, 1)
                last_month = this_month - datetime.timedelta(days=1)
                last_month_counts = self.get_queryset().filter(date__month=last_month.month, date__year=last_month.year,
                                                               event_id__in=artist_event_ids).total_counts()
                this_month_seconds = counts['seconds_played']
                last_month_seconds = last_month_counts['seconds_played']
                if last_month_seconds != 0:
                    counts['seconds_played_trend'] = ((this_month_seconds - last_month_seconds) / last_month_seconds) * 100
                else:
                    counts['seconds_played_trend'] = 'n/a'

                this_month_plays = counts['play_count']
                last_month_plays = last_month_counts['play_count']
                if last_month_plays != 0:
                    counts['play_count_trend'] = ((this_month_plays - last_month_plays) / last_month_plays) * 100
                else:
                    counts['play_count_trend'] = 'n/a'
        else:
            counts = qs.total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'] or 0)
        return counts

    def this_month_counts(self, artist_event_ids=None, trends=False, humanize=False):
        now = timezone.now()
        return self.monthly_counts(now.month, now.year, artist_event_ids=artist_event_ids,
                                   trends=trends, humanize=humanize)

    def this_month_counts_for_artist(self, artist_event_ids, humanize=False):
        now = timezone.now()
        return self.monthly_counts(now.month, now.year, artist_event_ids=artist_event_ids, humanize=humanize)

    def date_counts(self, month, year, artist_event_ids=None):
        """
        Returns a list of play counts and seconds played per day. If the requested month is the current
        month, return values only up to the current day (don't add zeroes for remaining months)
        """
        qs = self.get_queryset().filter(date__month=month, date__year=year)
        if artist_event_ids:
            if len(artist_event_ids) == 1:
                qs = qs.filter(event_id=artist_event_ids[0])
            else:
                qs = qs.filter(event_id__in=artist_event_ids)

        qs = qs.values('date', 'recording_type').order_by('date').total_counts_annotate()

        now = timezone.now().date()
        if now.month == month and now.year == year:
            days_in_month = now.day
        else:
            days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        audio_play_counts = {}
        audio_seconds_counts = {}
        video_play_counts = {}
        video_seconds_counts = {}
        for entry in qs:
            day = entry['date'].day
            if entry['recording_type'] == 'V':
                video_play_counts[day] = entry['play_count']
                video_seconds_counts[day] = entry['seconds_played']
            else:
                audio_play_counts[day] = entry['play_count']
                audio_seconds_counts[day] = entry['seconds_played']
        counts = {}
        counts['audio_plays_list'] = [audio_play_counts.get(day_number, 0) for day_number in days]
        counts['audio_seconds_list'] = [audio_seconds_counts.get(day_number, 0) for day_number in days]
        counts['video_plays_list'] = [video_play_counts.get(day_number, 0) for day_number in days]
        counts['video_seconds_list'] = [video_seconds_counts.get(day_number, 0) for day_number in days]
        counts['total_plays_list'] = [a+v for a, v in zip(counts['audio_plays_list'], counts['video_plays_list'])]
        counts['total_seconds_list'] = [a+v for a, v in zip(counts['audio_seconds_list'], counts['video_seconds_list'])]
        counts['dates'] = ["{0}/{1}".format(month, day) for day in days]
        return counts

    def create_random(self):
        today = timezone.now().date()
        params = {}
        params['date'] = today - datetime.timedelta(days=random.randrange(1, 90))
        params['recording_id'] = random.randrange(1, 10)
        params['user_id'] = random.randrange(1, 10)
        params['seconds_played'] = random.randrange(10, 600, 10)
        self.create(**params)

    def create_random_for_user(self, user_id):
        today = timezone.now()
        params = {}
        recordings = itertools.cycle([55, 81, 121, 166, 194])
        params['user_id'] = user_id
        for day in range(1, 90):
            params['date'] = (today - datetime.timedelta(days=day)).date()
            for i in range(1, 3):
                params['recording_id'] = next(recordings)  # Spike's and Ari's recordings
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
    event_id = models.PositiveIntegerField(blank=False)
    recording_type = models.CharField(max_length=1, choices=(('A', 'Audio'), ('V', 'Video')))

    objects = MetricsManager()

    class Meta:
        unique_together = ('recording_id', 'user_id', 'date')

    def __str__(self):
        return "V{0} U{1} D{2.year}/{2.month}/{2.day} C{3}".format(
            self.recording_id, self.user_id, self.date, self.seconds_played)
