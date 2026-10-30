from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rentals.models import Equipment, Booking, BookingEventLog
from rentals.services import BookingWorkflowService
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Наполнение базы демонстрационными бронированиями техники"

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser(
                "d_migda", "migda@mai.ru", "password123"
            )

        # Создаем второго студента для проверки изоляции данных (по ТЗ СРС №7)
        student2, _ = User.objects.get_or_create(
            username="student_mai", defaults={"email": "student@mai.ru"}
        )
        student2.set_password("student123")
        student2.save()

        # Данные для наполнения
        demo_data = [
            (
                "CAM-KMD-01",
                "Лукбук осенней коллекции бренда",
                "confirmed",
                0,
                3,
                user,
                "Съемка в павильоне, нужны 2 доп. аккумулятора",
            ),
            (
                "CAM-SNY-02",
                "Промо-ролик виллы в Дубае (Speedora)",
                "active",
                -1,
                2,
                user,
                "Выдано на выездную смену, комплект с верхней ручкой XLR",
            ),
            (
                "OPT-GM2-01",
                "Клип для инди-рок группы",
                "draft",
                2,
                5,
                user,
                "Требуется защитный ND-фильтр",
            ),
            (
                "LGT-AP12-01",
                "Интервью с деканом кафедры 317",
                "confirmed",
                1,
                2,
                user,
                "Комплект с октобоксом Light Dome",
            ),
            (
                "LGT-TUB-04",
                "Музыкальный лайв-перформанс",
                "returned",
                -5,
                -2,
                user,
                "Возвращено в полной комплектности, дефектов нет",
            ),
            (
                "CAM-BMP-03",
                "Дипломный короткометражный метр",
                "draft",
                3,
                7,
                student2,
                "Заявка второго студента (для теста изоляции)",
            ),
        ]

        created = 0
        for code, title, target_status, d_start, d_end, author, note in demo_data:
            eq = Equipment.objects.filter(inventory_code=code).first()
            if not eq:
                continue

            if Booking.objects.filter(project_title=title).exists():
                continue

            start = date.today() + timedelta(days=d_start)
            end = date.today() + timedelta(days=d_end)

            # Создаем через WorkflowService
            b = BookingWorkflowService.create_booking(
                user=author,
                equipment_id=eq.id,
                project_title=title,
                start_date=start,
                end_date=end,
                notes=note,
            )

            # Переводим в целевой статус по цепочке автомата
            if target_status == "confirmed":
                BookingWorkflowService.change_status(b.id, "confirmed", author)
            elif target_status == "active":
                BookingWorkflowService.change_status(b.id, "confirmed", author)
                BookingWorkflowService.change_status(b.id, "active", author)
            elif target_status == "returned":
                BookingWorkflowService.change_status(b.id, "confirmed", author)
                BookingWorkflowService.change_status(b.id, "active", author)
                BookingWorkflowService.change_status(b.id, "returned", author)

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Создано демонстрационных бронирований: {created}")
        )
