from devices.models import ProductionDevice, StorageDevice, ConsumptionDevice

DEVICE_TYPE_MAP = {
    "production": ProductionDevice,
    "storage": StorageDevice,
    "consumption": ConsumptionDevice,
}

def get_device_model_by_type(device_type: str):
    try:
        return DEVICE_TYPE_MAP[device_type.lower()]
    except KeyError:
        raise ValueError(f"Unsupported device_type: {device_type}")