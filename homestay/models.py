from django.db import models 
from django.contrib.auth.models import User
from django.utils import timezone 


# ===============================
# HOMESTAY
# ===============================
class Homestay(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)    

    name = models.CharField(max_length=200)
    description = models.TextField()
    district = models.CharField(max_length=100)

    price_per_night = models.IntegerField()

    latitude = models.FloatField()
    longitude = models.FloatField()

    image = models.ImageField(upload_to="homestays/", null=True, blank=True)
    is_approved = models.BooleanField(default=False) 

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    # 🔥 còn phòng hay không
    @property
    def has_empty_rooms(self):
        return self.room_set.filter(status="empty").exists()

    # 🔥 đếm phòng trống
    @property
    def empty_rooms_count(self):
        return self.room_set.filter(status="empty").count()


# ===============================
# ROOM
# ===============================
class Room(models.Model):

    homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE)

    room_number = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("empty", "Empty"),
            ("booked", "Booked"),
        ],
        default="empty"
    )

    def __str__(self):
        return f"{self.homestay.name} - Room {self.room_number}"


# ===============================
# BOOKING
# ===============================
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    guest_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)

    check_in = models.DateField()
    check_out = models.DateField()

    total_price = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest_name} - Room {self.room.room_number}"

    # 🔥 AUTO UPDATE ROOM STATUS
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.status in ["pending", "confirmed"]:
            self.room.status = "booked"
        else:
            self.room.status = "empty"

        self.room.save()


# ===============================
# REVIEW
# ===============================
class Review(models.Model):

    homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE, related_name="reviews")
    guest_name = models.CharField(max_length=200)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest_name} - {self.rating} Stars"