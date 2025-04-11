import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from devices.models import ProductionDevice, StorageDevice, ConsumptionDevice

User = get_user_model()

DEVICE_TYPES = {
    "production": ["Solar Panel", "Generator"],
    "storage": ["Battery", "Electric Vehicle"],
    "consumption": ["Air Conditioner", "Heater", "Electric Vehicle"],
}


def create_users(n=5):
    users = []
    for i in range(n):
        user, created = User.objects.get_or_create(
            username=f"user{i+1}",
            defaults={"email": f"user{i+1}@example.com"},
        )
        if created:
            user.set_password("password123")
            user.save()
        users.append(user)
    return users


def seed_devices_for_user(user):
    for _ in range(random.randint(1, 2)):
        name = random.choice(DEVICE_TYPES["production"])
        output = random.randint(1000, 5000)
        ProductionDevice.objects.create(
            name=name,
            user=user,
            is_solar=True if name==DEVICE_TYPES["production"][0] else False,
            status=random.choice(["online", "offline"]),
            instantaneous_output_watts=output,
        )

    for _ in range(random.randint(1, 2)):
        name = random.choice(DEVICE_TYPES["storage"])
        total_capacity = random.choice([20000, 32000, 50000])
        current_level = random.randint(0, total_capacity)
        StorageDevice.objects.create(
            name=name,
            user=user,
            status=random.choice(["online", "offline"]),
            total_capacity_wh=total_capacity,
            current_level_wh=current_level,
            charge_discharge_rate_watts=random.randint(-1000, 1000),
        )

    for _ in range(random.randint(1, 2)):
        name = random.choice(DEVICE_TYPES["consumption"])
        rate = random.randint(500, 3000)
        ConsumptionDevice.objects.create(
            name=name,
            user=user,
            status=random.choice(["online", "offline"]),
            consumption_rate_watts=rate,
        )


class Command(BaseCommand):
    help = "Seed the database with users and device data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding users and devices...")
        users = create_users(5)
        for user in users:
            seed_devices_for_user(user)
        self.stdout.write(self.style.SUCCESS("Done seeding!"))
