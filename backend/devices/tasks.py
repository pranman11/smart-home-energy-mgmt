from celery import shared_task
from .models import ProductionDevice, StorageDevice, ConsumptionDevice
from datetime import datetime
import random

@shared_task
def simulate_device_readings():
    # Simulate Production Devices
    for device in ProductionDevice.objects.filter(status="online"):
        device.instantaneous_output_watts = (
            random.randint(1000, 5000) if 6 <= datetime.now().hour <= 18 or not device.is_solar else 0
        )
        device.save(update_fields=["instantaneous_output_watts"])

    # Simulate Consumption Devices
    for device in ConsumptionDevice.objects.filter(status="online"):
        device.consumption_rate_watts = random.randint(500, 3000)
        device.save(update_fields=["consumption_rate_watts"])

    # Simulate Storage Devices
    for device in StorageDevice.objects.filter(status="online"):
        flow = random.randint(-1000, 1000)  # discharging or charging

        # Cap to boundaries
        new_level = device.current_level_wh + flow
        new_level = min(max(new_level, 0), device.total_capacity_wh)

        actual_flow = new_level - device.current_level_wh

        device.current_level_wh = new_level
        device.charge_discharge_rate_watts = actual_flow
        device.save(update_fields=["current_level_wh", "charge_discharge_rate_watts"])
