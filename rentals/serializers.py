from rest_framework import serializers
from .models import Equipment, Booking, BookingEventLog


class EquipmentSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = Equipment
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "inventory_code",
            "total_count",
            "available_count",
            "daily_rate",
            "image_name",
        ]


class BookingEventLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.username", read_only=True)
    timestamp_display = serializers.DateTimeField(
        source="timestamp", format="%d.%m.%Y %H:%M:%S", read_only=True
    )

    class Meta:
        model = BookingEventLog
        fields = [
            "id",
            "actor_name",
            "action_type",
            "old_status",
            "new_status",
            "comment",
            "timestamp_display",
        ]


class BookingSerializer(serializers.ModelSerializer):
    equipment_detail = EquipmentSerializer(source="equipment", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    audit_logs = BookingEventLogSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user_name",
            "equipment",
            "equipment_detail",
            "project_title",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "notes",
            "created_at",
            "audit_logs",
        ]
        read_only_fields = ["status", "user"]

    def validate_project_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Название проекта должно содержать не менее 5 символов."
            )
        return value.strip()
