from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, BookingViewSet, index_view

router = DefaultRouter()
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("", index_view, name="index"),
    path("api/rentals/", include(router.urls)),
]
