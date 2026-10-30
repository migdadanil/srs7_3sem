from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Equipment, Booking, BookingEventLog

ALLOWED_TRANSITIONS = {
    Booking.STATUS_DRAFT: [Booking.STATUS_CONFIRMED, Booking.STATUS_CANCELLED],
    Booking.STATUS_CONFIRMED: [Booking.STATUS_ACTIVE, Booking.STATUS_CANCELLED],
    Booking.STATUS_ACTIVE: [Booking.STATUS_RETURNED],
    Booking.STATUS_RETURNED: [],
    Booking.STATUS_CANCELLED: [],
}


class BookingWorkflowService:
    @staticmethod
    @transaction.atomic
    def create_booking(
        user, equipment_id, project_title, start_date, end_date, notes=""
    ):
        equipment = Equipment.objects.get(pk=equipment_id)

        booking = Booking.objects.create(
            user=user,
            equipment=equipment,
            project_title=project_title,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            status=Booking.STATUS_DRAFT,
        )

        BookingEventLog.objects.create(
            booking=booking,
            actor=user,
            action_type="INITIALIZE",
            old_status=None,
            new_status=Booking.STATUS_DRAFT,
            comment=f"Создан черновик заявки на {equipment.name} [{equipment.inventory_code}]",
        )
        return booking

    @staticmethod
    @transaction.atomic
    def change_status(booking_id, new_status, actor):
        booking = Booking.objects.select_for_update().get(pk=booking_id)
        current_status = booking.status

        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValidationError(
                f"Недопустимый переход: запрещено переводить из '{booking.get_status_display()}' "
                f"в '{dict(Booking.STATUS_CHOICES).get(new_status, new_status)}'."
            )

        equipment = Equipment.objects.select_for_update().get(pk=booking.equipment_id)

        if (
            current_status == Booking.STATUS_DRAFT
            and new_status == Booking.STATUS_CONFIRMED
        ):
            if equipment.available_count <= 0:
                raise ValidationError(
                    f"Недостаточно техники: все единицы '{equipment.name}' забронированы!"
                )
            equipment.available_count -= 1
            equipment.save(update_fields=["available_count"])

        elif current_status in [
            Booking.STATUS_CONFIRMED,
            Booking.STATUS_ACTIVE,
        ] and new_status in [Booking.STATUS_RETURNED, Booking.STATUS_CANCELLED]:
            if equipment.available_count < equipment.total_count:
                equipment.available_count += 1
                equipment.save(update_fields=["available_count"])

        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])

        BookingEventLog.objects.create(
            booking=booking,
            actor=actor,
            action_type="PHASE_SHIFT",
            old_status=current_status,
            new_status=new_status,
            comment=f"Статус изменен пользователем {actor.username}",
        )

        return booking
