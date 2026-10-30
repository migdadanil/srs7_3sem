from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ("camera", "Камеры и тушки"),
        ("optics", "Кинооптика"),
        ("light", "Студийный свет"),
        ("audio", "Звуковые системы"),
        ("grip", "Стабилизаторы и риги"),
    ]

    name = models.CharField(max_length=150, verbose_name="Наименование техники")
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="camera"
    )
    inventory_code = models.CharField(
        max_length=50, unique=True, verbose_name="Инвентарный шифр"
    )
    total_count = models.PositiveIntegerField(
        default=1, verbose_name="Всего на балансе"
    )
    available_count = models.PositiveIntegerField(
        default=1, verbose_name="Доступно сейчас"
    )
    daily_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00, verbose_name="Смена (руб)"
    )
    image_name = models.CharField(
        max_length=100, default="cam-komodo.png", verbose_name="Файл превью"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} [{self.inventory_code}] ({self.available_count}/{self.total_count})"

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Склад оборудования"


class Booking(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_CONFIRMED = "confirmed"
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Черновик заявки"),
        (STATUS_CONFIRMED, "Подтверждена (Бронь)"),
        (STATUS_ACTIVE, "Оборудование на съемке"),
        (STATUS_RETURNED, "Завершена (Возвращено)"),
        (STATUS_CANCELLED, "Отменена"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rent_bookings"
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, related_name="bookings"
    )
    project_title = models.CharField(
        max_length=200, verbose_name="Название медиапроекта"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата возврата")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    notes = models.TextField(blank=True, verbose_name="Технические заметки оператора")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование техники"
        verbose_name_plural = "Реестр бронирований"

    def __str__(self):
        return f"Бронь #{self.id}: {self.project_title} ({self.get_status_display()})"


class BookingEventLog(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="audit_logs"
    )
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Инициатор"
    )
    action_type = models.CharField(max_length=50, verbose_name="Тип действия")
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Событие аудита"
        verbose_name_plural = "Журнал аудита бронирований"
