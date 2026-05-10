from django.contrib import admin
from django.utils.html import format_html
from .models import Homestay, Room, Booking


@admin.register(Homestay)
class HomestayAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "district",
        "price_per_night",
        "latitude",
        "longitude",
        "image_preview",
    )

    list_filter = ("district",)
    search_fields = ("name", "district")
    list_per_page = 10

    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"

    image_preview.short_description = "Preview"


# ROOM ADMIN
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "room_number", "homestay")


# BOOKING ADMIN
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "guest_name", "check_in", "check_out", "status")