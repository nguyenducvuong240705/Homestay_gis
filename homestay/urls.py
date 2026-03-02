from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('api/homestays/', views.homestay_list, name='homestay_list'),
]