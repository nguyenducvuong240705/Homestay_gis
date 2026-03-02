from rest_framework import serializers
from .models import Homestay, Booking


class HomestaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Homestay
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'created_at']