from django.db import models
from django.contrib.auth.models import User


class Homestay(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    price_per_night = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='homestays/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    homestay = models.ForeignKey(
        Homestay,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.homestay.name}"