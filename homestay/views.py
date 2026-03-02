from django.shortcuts import render
from django.http import JsonResponse
from .models import Homestay


def index(request):
    return render(request, "index.html")


def homestay_list(request):
    homestays = Homestay.objects.all()

    search = request.GET.get("search")
    district = request.GET.get("district")

    if search:
        homestays = homestays.filter(name__icontains=search)

    if district:
        homestays = homestays.filter(district__icontains=district)

    data = [
        {
            "id": h.id,
            "name": h.name,
            "price": h.price_per_night,
            "district": h.district,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "image": h.image.url if h.image else ""
        }
        for h in homestays
    ]

    return JsonResponse({
        "count": len(data),
        "results": data
    })