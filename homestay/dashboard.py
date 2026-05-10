from django.db.models import Avg, Max, Count
from .models import Homestay


def get_dashboard_data():

    total = Homestay.objects.count()

    avg_price = Homestay.objects.aggregate(
        Avg("price_per_night")
    )["price_per_night__avg"] or 0

    max_price = Homestay.objects.aggregate(
        Max("price_per_night")
    )["price_per_night__max"] or 0

    by_district = (
        Homestay.objects
        .values("district")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return {
        "total": total,
        "avg_price": int(avg_price),
        "max_price": max_price,
        "by_district": list(by_district)
    }