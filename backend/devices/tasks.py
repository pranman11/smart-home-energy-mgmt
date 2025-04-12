from celery import shared_task
from .models import ProductionDevice, StorageDevice, ConsumptionDevice
from django.contrib.auth import get_user_model
from datetime import datetime
import random
import redis
import json
import time

User = get_user_model()

# Connect to Redis
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

@shared_task
def simulate_device_readings():
    user_stats = {}

    # Simulate Production Devices
    for device in ProductionDevice.objects.filter(status="online"):
        production = (
            random.randint(1000, 5000) if 6 <= datetime.now().hour <= 18 or not device.is_solar else 0
        )
        device.instantaneous_output_watts = production
        device.save(update_fields=["instantaneous_output_watts"])

        uid = device.user_id
        stats = get_or_init_user_stats(user_stats, device.user_id)
        stats["production"] += production

    # Simulate Consumption Devices
    for device in ConsumptionDevice.objects.filter(status="online"):
        consumption = random.randint(500, 3000)
        device.consumption_rate_watts = consumption
        device.save(update_fields=["consumption_rate_watts"])

        uid = device.user_id
        stats = get_or_init_user_stats(user_stats, device.user_id)
        user_stats[uid]["consumption"] += consumption

    # Simulate Storage Devices
    for device in StorageDevice.objects.filter(status="online"):
        flow = random.randint(-1000, 1000)
        new_level = device.current_level_wh + flow
        new_level = min(max(new_level, 0), device.total_capacity_wh)
        actual_flow = new_level - device.current_level_wh

        device.current_level_wh = new_level
        device.charge_discharge_rate_watts = actual_flow
        device.save(update_fields=["current_level_wh", "charge_discharge_rate_watts"])

        uid = device.user_id

        stats = get_or_init_user_stats(user_stats, device.user_id)
        stats["storage_total"] += device.total_capacity_wh
        stats["storage_level"] += new_level
        stats["storage_flow"] += actual_flow
        stats["storage_count"] += 1

    # Compute and store final energy stats per user 
    for uid, stats in user_stats.items():
        current_production = stats.get("production", 0)
        current_consumption = stats.get("consumption", 0)
        total_capacity_wh = stats.get("storage_total", 0)
        current_level_wh = stats.get("storage_level", 0)
        flow = stats.get("storage_flow", 0)
        count = stats.get("storage_count", 0)

        energy_stats = {
            "current_production": current_production,
            "current_consumption": current_consumption,
            "current_storage": {
                "total_capacity_wh": total_capacity_wh,
                "current_level_wh": current_level_wh,
                "percentage": (current_level_wh / total_capacity_wh) * 100 if total_capacity_wh else 0
            },
            "current_storage_flow": flow,
            "net_grid_flow": current_consumption - current_production - flow,
            "timestamp": int(time.time())
        }

        r.set(f"energy_stats:{uid}", json.dumps(energy_stats))

def get_or_init_user_stats(user_stats, uid):
    return user_stats.setdefault(uid, {
        "production": 0,
        "consumption": 0,
        "storage_total": 0,
        "storage_level": 0,
        "storage_flow": 0,
        "storage_count": 0,
    })