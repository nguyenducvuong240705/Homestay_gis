from django.shortcuts import render

HOMESTAYS = [
    {
        "id": 1,
        "name": "Homestay Quận 1",
        "district": "Quận 1",
        "lat": 10.776889,
        "lng": 106.700806,
        "price": 500000,
        "desc": "Gần trung tâm"
    },
    {
        "id": 2,
        "name": "Homestay Quận 3",
        "district": "Quận 3",
        "lat": 10.780087,
        "lng": 106.682225,
        "price": 450000,
        "desc": "Yên tĩnh"
    },
    {
        "id": 3,
        "name": "Homestay Thủ Đức",
        "district": "Thủ Đức",
        "lat": 10.849320,
        "lng": 106.753770,
        "price": 400000,
        "desc": "Gần làng đại học"
    }
]

def home(request):
    return render(request, "home.html")

def detail(request, id):
    hs = next(h for h in HOMESTAYS if h["id"] == id)
    return render(request, "detail.html", {"h": hs})
