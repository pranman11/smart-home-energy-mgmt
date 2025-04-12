import strawberry
import redis
import json
from typing import Optional

from devices.models import ProductionDevice, ConsumptionDevice, StorageDevice
from devices.graphql.types import DeviceType, EnergyStats, StorageStats

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

@strawberry.type
class Query:

    @strawberry.field
    def all_devices(self, info) -> list[DeviceType]:
        '''
            allDevices API that returns a list of all devices for logged in user with device details
        '''
        user = info.context.request.user
        print(user.username)
        devices = list(ProductionDevice.objects.filter(user=user)) + \
                  list(StorageDevice.objects.filter(user=user)) + \
                  list(ConsumptionDevice.objects.filter(user=user))
        
        return devices

    @strawberry.field
    def energy_stats(self, info) -> Optional[EnergyStats]:
        '''
            energyStats API that returns computed stats for logged in user
        '''
        user = info.context.request.user
        key = f"energy_stats:{user.id}"

        data = r.get(key)
        if not data:
            return None  #TODO: raise a custom error or fallback to DB logic

        parsed = json.loads(data)

        return EnergyStats(
            current_production=parsed["current_production"],
            current_consumption=parsed["current_consumption"],
            current_storage=StorageStats(**parsed["current_storage"]),
            current_storage_flow=parsed["current_storage_flow"],
            net_grid_flow=parsed["net_grid_flow"],
            timestamp=parsed["timestamp"]
        )
