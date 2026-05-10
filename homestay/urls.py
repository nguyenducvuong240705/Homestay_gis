from django.urls import path
from . import views

urlpatterns = [
    # ==================== TRANG CHÍNH ====================
    path('', views.index, name='home'),
    path('map/', views.map_view, name='map'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # ==================== HOMESTAY ====================
    path('homestay/<int:id>/', views.homestay_detail, name='detail'),
    path('api/homestays/', views.homestay_api, name='api_homestays'),
    path('api/rooms/<int:homestay_id>/', views.room_api, name='room_api'),
    path('submit-review/<int:id>/', views.submit_review, name='submit_review'),

    # ==================== USER ====================
    path('user/', views.user_profile, name='user_profile'),

    # ==================== AUTH ====================
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ==================== LOOKUP ====================
    path('lookup/', views.lookup_booking, name='lookup_booking'),

    # ==================== BOOKING ====================
    path('booking/<int:id>/', views.booking, name='booking'),
    path('success/<int:booking_id>/', views.success, name='success'),
    path('api/book-room/', views.book_room, name='book_room'),

    # ==================== DASHBOARD ====================
    path('dashboard/', views.dashboard, name='manage'),
    path('dashboard/bookings/', views.dashboard_bookings, name='dashboard_bookings'),
    path('dashboard/revenue/', views.dashboard_revenue, name='dashboard_revenue'),
    path('dashboard/homestays/', views.dashboard_homestays, name='dashboard_homestays'),
    path('dashboard/approve-homestays/', views.dashboard_approve_homestays, name='dashboard_approve_homestays'),

    # ==================== DUYỆT HOMESTAY ====================
    path('dashboard/approve/<int:id>/', views.approve_homestay, name='approve_homestay'),
    path('dashboard/reject/<int:id>/', views.reject_homestay, name='reject_homestay'),

    # ==================== ROUTE CŨ - GIỮ LẠI ====================
    path('approve/<int:id>/', views.approve_homestay, name='approve_homestay_old'),
    path('reject/<int:id>/', views.reject_homestay, name='reject_homestay_old'),

    # ==================== CRUD HOMESTAY ====================
    path('add/', views.add_homestay, name='add_homestay'),
    path('edit/<int:id>/', views.edit_homestay, name='edit_homestay'),
    path('delete/<int:id>/', views.delete_homestay, name='delete_homestay'),

    # ==================== BOOKING ADMIN ====================
    path('approve-booking/<int:id>/', views.accept_booking, name='approve_booking'),
    path('reject-booking/<int:id>/', views.reject_booking, name='reject_booking'),
]