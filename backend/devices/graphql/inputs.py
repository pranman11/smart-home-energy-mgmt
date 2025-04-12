import strawberry
from typing import Optional

@strawberry.input
class DeviceInput:
    '''
        Input for createDevice endpoint
    '''
    name: str
    status: str
    device_type: str  # "production", "storage", "consumption"

    # Subclass-specific optional fields
    instantaneous_output_watts: Optional[int] = None  # Production
    total_capacity_wh: Optional[int] = None           # Storage
    current_level_wh: Optional[int] = None            # Storage
    charge_discharge_rate_watts: Optional[int] = None # Storage
    consumption_rate_watts: Optional[int] = None      # Consumption



@strawberry.input
class DeviceUpdateInput:
    '''
        Input for updateDevice endpoint
    '''
    id: int
    device_type: str  # "production", "storage", "consumption"
    name: Optional[str] = None
    status: Optional[str] = None

    # subclass-specific (optional)
    instantaneous_output_watts: Optional[int] = None
    total_capacity_wh: Optional[int] = None
    current_level_wh: Optional[int] = None
    charge_discharge_rate_watts: Optional[int] = None
    consumption_rate_watts: Optional[int] = None

