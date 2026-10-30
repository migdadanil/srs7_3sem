from django.contrib import admin
from .models import Equipment, Booking, BookingEventLog


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "inventory_code",
        "available_count",
        "total_count",
        "daily_rate",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "inventory_code")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project_title",
        "user",
        "equipment",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status",)


@admin.register(BookingEventLog)
class BookingEventLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "actor",
        "action_type",
        "old_status",
        "new_status",
        "timestamp",
    )
