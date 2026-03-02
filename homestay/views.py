from django.shortcuts import render, redirect, get_object_or_404
from .models import Homestay, Booking


# Trang chủ
def home(request):
    return render(request, 'home.html')


# Trang bản đồ
def map_view(request):
    homestays = Homestay.objects.all()
    return render(request, 'map.html', {'homestays': homestays})


# Trang đặt phòng
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Homestay


def booking(request):
    homestays = Homestay.objects.all()

    if request.method == "POST":
        homestay_id = request.POST.get("homestay")
        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        homestay = get_object_or_404(Homestay, id=homestay_id)

        booking = Booking.objects.create(
            homestay=homestay,
            customer_name=customer_name,
            phone=phone,
            check_in=check_in,
            check_out=check_out
        )

        return redirect("success", booking_id=booking.id)

    return render(request, "booking.html", {"homestays": homestays})


def success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "success.html", {"booking": booking})
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Homestay


def manage_bookings(request):
    bookings = Booking.objects.all().order_by("-created_at")
    return render(request, "manage.html", {"bookings": bookings})


def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect("manage_bookings")


def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    homestays = Homestay.objects.all()

    if request.method == "POST":
        booking.homestay_id = request.POST.get("homestay")
        booking.customer_name = request.POST.get("customer_name")
        booking.phone = request.POST.get("phone")
        booking.check_in = request.POST.get("check_in")
        booking.check_out = request.POST.get("check_out")
        booking.save()
        return redirect("manage_bookings")

    return render(request, "edit_booking.html", {
        "booking": booking,
        "homestays": homestays
    })
def manage_bookings(request):
    bookings = Booking.objects.all().order_by("-created_at")
    return render(request, "manage_bookings.html", {
        "bookings": bookings
    })



# Trang quản lý
def manage(request):
    homestays = Homestay.objects.all()
    bookings = Booking.objects.all().order_by("-created_at")

    return render(request, "manage.html", {
        "homestays": homestays,
        "bookings": bookings,
    })


# Thêm khách sạn
def add_homestay(request):
    if request.method == "POST":
        Homestay.objects.create(
            name=request.POST.get("name"),
            address=request.POST.get("address"),
            district=request.POST.get("district"),
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
            price=request.POST.get("price"),
            description=request.POST.get("description"),
        )
        return redirect('manage')

    return render(request, 'add.html')


# Sửa khách sạn
def edit_homestay(request, id):
    homestay = get_object_or_404(Homestay, id=id)

    if request.method == "POST":
        homestay.name = request.POST.get("name")
        homestay.address = request.POST.get("address")
        homestay.district = request.POST.get("district")
        homestay.latitude = request.POST.get("latitude")
        homestay.longitude = request.POST.get("longitude")
        homestay.price = request.POST.get("price")
        homestay.description = request.POST.get("description")
        homestay.save()
        return redirect('manage')

    return render(request, 'edit.html', {'h': homestay})


# Xóa khách sạn
def delete_homestay(request, id):
    homestay = get_object_or_404(Homestay, id=id)
    homestay.delete()
    return redirect('manage')
def approve_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "approved"
    booking.save()
    return redirect("manage")


def reject_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "rejected"
    booking.save()
    return redirect("manage")