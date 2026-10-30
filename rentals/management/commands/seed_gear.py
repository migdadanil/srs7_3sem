from django.core.management.base import BaseCommand
from rentals.models import Equipment


class Command(BaseCommand):
    help = "Первичное наполнение склада оборудования MediaLab для СРС №7"

    def handle(self, *args, **options):
        items = [
            {
                "name": "RED Komodo 6K Cine Rig",
                "category": "camera",
                "inventory_code": "CAM-KMD-01",
                "total_count": 2,
                "available_count": 2,
                "daily_rate": 8500.00,
                "image_name": "cam-komodo.png",
            },
            {
                "name": "Sony Cinema Line Rig + Top Handle",
                "category": "camera",
                "inventory_code": "CAM-SNY-02",
                "total_count": 3,
                "available_count": 3,
                "daily_rate": 6000.00,
                "image_name": "cam-sony-fx.png",
            },
            {
                "name": "Blackmagic Pocket Cinema 6K Pro",
                "category": "camera",
                "inventory_code": "CAM-BMP-03",
                "total_count": 2,
                "available_count": 2,
                "daily_rate": 4500.00,
                "image_name": "cam-blackmagic.png",
            },
            {
                "name": "ARRI Alexa Mini Gimbal System",
                "category": "grip",
                "inventory_code": "GRP-ARR-01",
                "total_count": 1,
                "available_count": 1,
                "daily_rate": 15000.00,
                "image_name": "rig-arri.png",
            },
            {
                "name": "Sony FE 24-70mm f/2.8 GM II",
                "category": "optics",
                "inventory_code": "OPT-GM2-01",
                "total_count": 4,
                "available_count": 4,
                "daily_rate": 2500.00,
                "image_name": "opt-gmaster.png",
            },
            {
                "name": "Aputure Light Storm 1200d Pro",
                "category": "light",
                "inventory_code": "LGT-AP12-01",
                "total_count": 2,
                "available_count": 2,
                "daily_rate": 5000.00,
                "image_name": "lgt-aputure.png",
            },
            {
                "name": "Pixel RGB Studio Tube Light",
                "category": "light",
                "inventory_code": "LGT-TUB-04",
                "total_count": 6,
                "available_count": 6,
                "daily_rate": 1200.00,
                "image_name": "lgt-tube.png",
            },
            {
                "name": "DJI Mic 2 Wireless Transmitter Kit",
                "category": "audio",
                "inventory_code": "SND-DJI-01",
                "total_count": 3,
                "available_count": 3,
                "daily_rate": 1800.00,
                "image_name": "snd-dji-mic.png",
            },
        ]

        created_count = 0
        for item in items:
            obj, created = Equipment.objects.get_or_create(
                inventory_code=item["inventory_code"], defaults=item
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Склад синхронизирован. Создано позиций: {created_count}"
            )
        )
