from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.map_view, name='map'),
    path('booking/', views.booking, name='booking'),
    path('success/<int:booking_id>/', views.success, name='success'),

    # QUẢN LÝ
    path('manage/', views.manage, name='manage'),
    path('approve/<int:id>/', views.approve_booking, name='approve_booking'),
    path('reject/<int:id>/', views.reject_booking, name='reject_booking'),

    path('add/', views.add_homestay, name='add'),
    path('edit/<int:id>/', views.edit_homestay, name='edit'),
    path('delete/<int:id>/', views.delete_homestay, name='delete'),
]