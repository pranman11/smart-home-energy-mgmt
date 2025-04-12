import strawberry_django
import strawberry
from strawberry import auto
from strawberry.scalars import JSON

from devices.models import Device, ProductionDevice, ConsumptionDevice, StorageDevice

@strawberry_django.type(Device)
class DeviceType:
    id: auto
    name: auto
    status: auto

    @strawberry.field
    def device_type(self) -> str:
        return self.__class__.__name__.replace("Device", "").lower()
    
    @strawberry.field
    def other_details(self) -> JSON:
        if isinstance(self, ProductionDevice):
            return {
                "instantaneous_output_watts": self.instantaneous_output_watts,
            }
        elif isinstance(self, StorageDevice):
            return {
                "total_capacity_wh": self.total_capacity_wh,
                "current_level_wh": self.current_level_wh,
                "charge_discharge_rate_watts": self.charge_discharge_rate_watts,
            }
        elif isinstance(self, ConsumptionDevice):
            return {
                "consumption_rate_watts": self.consumption_rate_watts,
            }
        return {}

@strawberry.type
class StorageStats:
    total_capacity_wh: int
    current_level_wh: int
    percentage: float

@strawberry.type
class EnergyStats:
    current_production: int
    current_consumption: int
    current_storage: StorageStats
    current_storage_flow: int
    net_grid_flow: int
    timestamp: int
