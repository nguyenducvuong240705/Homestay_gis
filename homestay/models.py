from django.db import models

from django.db import models

class Homestay(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    price = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

