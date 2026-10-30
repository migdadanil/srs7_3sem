from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import Equipment, Booking
from .serializers import EquipmentSerializer, BookingSerializer
from .services import BookingWorkflowService


def index_view(request):
    """Главный экран Single-Page интерфейса Nothing . Rent"""
    return render(request, "rentals/index.html")


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipment.objects.filter(is_active=True)
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related("equipment", "user").prefetch_related(
            "audit_logs"
        )

        # Изоляция доступа: студент видит только свои заявки, персонал — все
        if not user.is_staff:
            qs = qs.filter(user=user)

        # Два серверных параметра фильтрации (по ТЗ СРС №7)
        status_param = self.request.query_params.get("status")
        category_param = self.request.query_params.get("category")

        if status_param:
            qs = qs.filter(status=status_param)
        if category_param:
            qs = qs.filter(equipment__category=category_param)

        return qs

    def perform_create(self, serializer):
        data = serializer.validated_data
        booking = BookingWorkflowService.create_booking(
            user=self.request.user,
            equipment_id=data["equipment"].id,
            project_title=data["project_title"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            notes=data.get("notes", ""),
        )
        serializer.instance = booking

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        booking = self.get_object()
        target_status = request.data.get("target_status")

        if not target_status:
            return Response(
                {"error": "Не передан целевой статус target_status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_booking = BookingWorkflowService.change_status(
                booking_id=booking.id, new_status=target_status, actor=request.user
            )
            return Response(
                BookingSerializer(updated_booking).data, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        if instance.status in [Booking.STATUS_CONFIRMED, Booking.STATUS_ACTIVE]:
            eq = instance.equipment
            eq.available_count += 1
            eq.save()
        instance.delete()
