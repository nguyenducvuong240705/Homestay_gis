from django.contrib import admin
from .models import Homestay, Booking


@admin.register(Homestay)
class HomestayAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'price_per_night', 'created_at')
    search_fields = ('name', 'district')
    list_filter = ('district',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'homestay', 'check_in', 'check_out', 'guests')
    list_filter = ('check_in',)