from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .models import UserVideoMetric
from .serializers import UserVideoMetricSerializer


class MetricView(generics.CreateAPIView):
    model = UserVideoMetric
    serializer_class = UserVideoMetricSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            try:
                now = timezone.now()
                metric = UserVideoMetric.objects.select_for_update().get(
                    media_id=serializer.validated_data.get('media_id'),
                    user_id=serializer.validated_data.get('user_id'),
                    date=now.date()
                )
                if self.passes_validation(now, metric):
                    http_status = status.HTTP_204_NO_CONTENT
                    metric.seconds_played = F('seconds_played') + settings.PING_INTERVAL
                    metric.last_ping = now
                    metric.save()
                else:
                    http_status = status.HTTP_403_FORBIDDEN
            except UserVideoMetric.DoesNotExist:
                self.perform_create(serializer)
                http_status = status.HTTP_201_CREATED
        return Response(status=http_status)

    def passes_validation(self, now, metric):
        allowed_ping_interval = (now >= (metric.last_ping + timedelta(seconds=settings.PING_INTERVAL)))
        less_than_daily_limit = metric.seconds_played <= settings.DAILY_LIMIT_PER_MEDIA
        return allowed_ping_interval and less_than_daily_limit

    def perform_create(self, serializer):
        serializer.save()

metric_view = MetricView.as_view()
