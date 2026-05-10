from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Homestay, Booking, Room, Review
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail


# ==================== PHÂN QUYỀN ADMIN CUSTOM ====================
def admin_required(view_func):
    return login_required(
        user_passes_test(lambda u: u.is_staff, login_url="/admin-login/")(view_func),
        login_url="/admin-login/"
    )


# ==================== HÀM PHỤ TRỢ ====================
def get_active_booking_room_ids(homestay):
    return Booking.objects.filter(
        homestay=homestay,
        status__in=["pending", "confirmed"]
    ).exclude(room__isnull=True).values_list("room_id", flat=True)


def get_real_empty_rooms_count(homestay):
    total_rooms = Room.objects.filter(homestay=homestay).count()
    booked_room_ids = set(get_active_booking_room_ids(homestay))
    return max(total_rooms - len(booked_room_ids), 0)


def has_real_empty_rooms(homestay):
    return get_real_empty_rooms_count(homestay) > 0


# ==================== TRANG CHÍNH ====================
def index(request):
    homestays = Homestay.objects.all()[:5]

    homestay_cards = []
    for h in homestays:
        empty_rooms_count = get_real_empty_rooms_count(h)

        homestay_cards.append({
            "id": h.id,
            "name": h.name,
            "district": h.district,
            "image": h.image if getattr(h, "image", None) else None,
            "has_empty_rooms": empty_rooms_count > 0,
            "empty_rooms_count": empty_rooms_count,
        })

    return render(request, "index.html", {
        "homestays": homestay_cards
    })


def map_view(request):
    return render(request, "map.html")


# ==================== HOMESTAY ====================
def homestay_detail(request, id):
    homestay = Homestay.objects.get(id=id)

    empty_rooms = get_real_empty_rooms_count(homestay)
    reviews = homestay.reviews.order_by("-created_at")

    return render(request, "detail.html", {
        "homestay": homestay,
        "empty_rooms": empty_rooms,
        "reviews": reviews
    })


# ==================== USER ====================
@login_required
def user_profile(request):
    if request.method == "POST":
        Homestay.objects.create(
            name=request.POST.get("name"),
            district=request.POST.get("district"),
            price_per_night=request.POST.get("price"),
            image=request.FILES.get("image"),
            owner=request.user,
            is_approved=False,
            latitude=10.7769,
            longitude=106.7009
        )

        messages.success(request, "🎉 Đăng thành công!")
        return redirect("/user/")

    user_bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    my_homestays = Homestay.objects.filter(owner=request.user).order_by("-id")

    return render(request, "user.html", {
        "user_bookings": user_bookings,
        "my_homestays": my_homestays
    })


# ==================== BOOKING ====================
@login_required
def booking(request, id):
    homestay = Homestay.objects.get(id=id)

    return render(request, "booking.html", {
        "homestay": homestay
    })


def success(request, booking_id):
    return render(request, "success.html", {
        "booking_id": booking_id
    })


# ==================== API ====================
def homestay_api(request):
    search = request.GET.get("search", "")
    district = request.GET.get("district", "")
    price = request.GET.get("price")

    homestays = Homestay.objects.all()

    if search:
        homestays = homestays.filter(name__icontains=search)

    if district:
        homestays = homestays.filter(district=district)

    if price:
        homestays = homestays.filter(price_per_night__lte=price)

    data = []

    for h in homestays:
        empty_rooms_count = get_real_empty_rooms_count(h)

        data.append({
            "id": h.id,
            "name": h.name,
            "description": h.description,
            "district": h.district,
            "price": h.price_per_night,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "image": h.image.url if h.image else "",
            "has_empty_rooms": empty_rooms_count > 0,
            "empty_rooms_count": empty_rooms_count
        })

    return JsonResponse(data, safe=False)


def room_api(request, homestay_id):
    rooms = Room.objects.filter(homestay_id=homestay_id)

    data = []
    for r in rooms:
        booked = Booking.objects.filter(
            room=r,
            status__in=["pending", "confirmed"]
        ).exists()

        data.append({
            "id": r.id,
            "room_number": r.room_number,
            "price": r.homestay.price_per_night,
            "status": "booked" if booked else "empty"
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def book_room(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        data = json.loads(request.body)

        homestay = Homestay.objects.get(id=data["room_id"])

        active_room_ids = Booking.objects.filter(
            homestay=homestay,
            status__in=["pending", "confirmed"]
        ).exclude(room__isnull=True).values_list("room_id", flat=True)

        room = homestay.room_set.exclude(id__in=active_room_ids).first()

        if not room:
            return JsonResponse({"error": "No empty room"}, status=400)

        booking = Booking.objects.create(
            user=request.user,
            homestay=homestay,
            room=room,
            guest_name=data["name"],
            phone=data["phone"],
            check_in=data["checkin"],
            check_out=data["checkout"],
            total_price=homestay.price_per_night,
            status="pending"
        )

        room.status = "booked"
        room.save()

        return JsonResponse({
            "message": "booking created",
            "booking_id": booking.id
        })

    return JsonResponse({"error": "invalid request"})


# ==================== REVIEW ====================
@csrf_exempt
@login_required
def submit_review(request, id):
    if request.method == "POST":
        homestay = Homestay.objects.get(id=id)

        Review.objects.create(
            homestay=homestay,
            guest_name=request.POST.get("guest_name", "Anonymous"),
            rating=int(request.POST.get("rating", 5)),
            comment=request.POST.get("comment", "")
        )

        return redirect(f"/homestay/{id}/")

    return redirect("/")


# ==================== LOOKUP ====================
def lookup_booking(request):
    phone = request.GET.get("phone", "")
    bookings = None

    if phone:
        bookings = Booking.objects.filter(
            phone__icontains=phone
        ).order_by("-created_at")

    return render(request, "lookup.html", {
        "bookings": bookings,
        "phone": phone
    })


# ==================== DASHBOARD ====================
@admin_required
def dashboard(request):
    total_booking = Booking.objects.count()
    total_revenue = sum(
        b.total_price for b in Booking.objects.filter(status="confirmed") if b.total_price
    )
    total_homestay = Homestay.objects.count()

    recent_bookings = Booking.objects.select_related("homestay", "room", "user").order_by("-created_at")[:10]

    return render(request, "dashboard.html", {
        "page": "overview",
        "total_booking": total_booking,
        "total_revenue": total_revenue,
        "total_homestay": total_homestay,
        "recent_bookings": recent_bookings,
    })


@admin_required
def dashboard_bookings(request):
    bookings = Booking.objects.select_related("homestay", "room", "user").order_by("-created_at")

    paginator = Paginator(bookings, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard.html", {
        "page": "bookings",
        "page_obj": page_obj
    })


@admin_required
def dashboard_approve_homestays(request):
    homestays = Homestay.objects.filter(is_approved=False).order_by("-created_at")

    paginator = Paginator(homestays, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "approve_homestays.html", {
        "page_obj": page_obj
    })


@admin_required
def dashboard_revenue(request):
    bookings = Booking.objects.filter(status="confirmed").select_related("homestay", "room", "user").order_by("-created_at")

    paginator = Paginator(bookings, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    total = sum(b.total_price for b in bookings if b.total_price)

    return render(request, "dashboard.html", {
        "page": "revenue",
        "page_obj": page_obj,
        "total": total
    })


@admin_required
def dashboard_homestays(request):
    homestays = Homestay.objects.all().order_by("-id")

    paginator = Paginator(homestays, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard.html", {
        "page": "homestays",
        "page_obj": page_obj
    })


# ==================== CONTACT / ABOUT ====================
def contact(request):
    success = False

    if request.method == "POST":
        success = True

    return render(request, "contact.html", {"success": success})


def about(request):
    return render(request, "about.html")


# ==================== ADMIN ACTION ====================
@admin_required
def accept_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "confirmed"
    booking.save()

    if booking.room:
        booking.room.status = "booked"
        booking.room.save()

    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("/dashboard/")


@admin_required
def reject_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "rejected"
    booking.save()

    if booking.room:
        has_active_booking = Booking.objects.filter(
            room=booking.room,
            status__in=["pending", "confirmed"]
        ).exclude(id=booking.id).exists()

        if not has_active_booking:
            booking.room.status = "empty"
            booking.room.save()

    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("/dashboard/")


@admin_required
def approve_homestay(request, id):
    h = get_object_or_404(Homestay, id=id)
    h.is_approved = True
    h.save()

    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("dashboard_approve_homestays")


@admin_required
def reject_homestay(request, id):
    h = get_object_or_404(Homestay, id=id)
    h.is_approved = False
    h.save()

    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("dashboard_approve_homestays")


def add_homestay(request):
    return render(request, "add.html")


def edit_homestay(request, id):
    return render(request, "edit.html")


def delete_homestay(request, id):
    return redirect("/dashboard/")


# ==================== AUTH ====================
def register_view(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("/")

    return render(request, "register.html", {"form": form})


def login_view(request):
    form = AuthenticationForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        if user.is_staff:
            return redirect("/dashboard/")
        return redirect("/")

    return render(request, "login.html", {
        "form": form,
        "page_title": "Đăng nhập hệ thống"
    })


def admin_login_view(request):
    form = AuthenticationForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        if not user.is_staff:
            messages.error(request, "Tài khoản này không có quyền quản trị.")
            return render(request, "login.html", {
                "form": form,
                "page_title": "Đăng nhập Admin"
            })

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "login.html", {
        "form": form,
        "page_title": "Đăng nhập Admin"
    })


def logout_view(request):
    logout(request)
    return redirect("/")