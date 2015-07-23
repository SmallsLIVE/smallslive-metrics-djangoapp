from rest_framework import serializers
from .models import UserVideoMetric


class UserVideoMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideoMetric
        validators = []
