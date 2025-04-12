import strawberry
from django.core.exceptions import ObjectDoesNotExist

from devices.models import ConsumptionDevice, StorageDevice, ProductionDevice
from devices.graphql.types import DeviceType
from devices.graphql.inputs import DeviceInput, DeviceUpdateInput
from devices.utils import get_device_model_by_type

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_device(self, info, input: DeviceInput) -> DeviceType:
        '''
            createDevice API: creates a new device and validates request details for logged in user 
        '''
        user = info.context.request.user

        # check whether device type is a valid type
        valid_types = {"production", "storage", "consumption"}
        if input.device_type not in valid_types:
            raise ValueError(f"Invalid device_type '{input.device_type}'. Must be one of: {valid_types}")

        if input.status not in ["online", "offline"]:
            raise ValueError("Status must be either 'online' or 'offline'")

        if input.device_type == "production":
            # validate that request contains only instantaneous output values for production devices
            if input.instantaneous_output_watts is None:
                raise ValueError("instantaneous_output_watts is required for production devices")
            if any([
                input.total_capacity_wh,
                input.current_level_wh,
                input.charge_discharge_rate_watts,
                input.consumption_rate_watts
            ]):
                raise ValueError("Only instantaneous_output_watts is allowed for production devices")
            
            device = ProductionDevice.objects.create(
                user=user,
                name=input.name,
                status=input.status,
                instantaneous_output_watts=input.instantaneous_output_watts,
                is_solar=input.is_solar,
            )

        elif input.device_type == "storage":
             # validate that request contains only capacity, current level and charge/discharge rate values for storage devices
            if None in (input.total_capacity_wh, input.current_level_wh, input.charge_discharge_rate_watts):
                raise ValueError("total_capacity_wh, current_level_wh, and charge_discharge_rate_watts are required for storage devices")
            if any([
                input.instantaneous_output_watts,
                input.consumption_rate_watts
            ]):
                raise ValueError("Invalid fields for storage devices")
            if input.current_level_wh > input.total_capacity_wh:
                raise ValueError("current_level_wh cannot exceed total_capacity_wh")

            device = StorageDevice.objects.create(
                user=user,
                name=input.name,
                status=input.status,
                total_capacity_wh=input.total_capacity_wh,
                current_level_wh=input.current_level_wh,
                charge_discharge_rate_watts=input.charge_discharge_rate_watts,
            )

        elif input.device_type == "consumption":
             # validate that request contains only consumption rate values for consumption devices
            if input.consumption_rate_watts is None:
                raise ValueError("consumption_rate_watts is required for consumption devices")
            if any([
                input.instantaneous_output_watts,
                input.total_capacity_wh,
                input.current_level_wh,
                input.charge_discharge_rate_watts
            ]):
                raise ValueError("Only consumption_rate_watts is allowed for consumption devices")

            device = ConsumptionDevice.objects.create(
                user=user,
                name=input.name,
                status=input.status,
                consumption_rate_watts=input.consumption_rate_watts,
            )

        return device
    
    @strawberry.mutation
    def update_device(self, info, input: DeviceUpdateInput) -> DeviceType:
        user = info.context.request.user

        valid_types = {"production", "storage", "consumption"}
        if input.device_type not in valid_types:
            raise ValueError(f"Invalid device_type '{input.device_type}'. Must be one of: {valid_types}")

        # Get correct subclass model
        model_class = get_device_model_by_type(input.device_type)

        try:
            device = model_class.objects.get(id=input.id, user=user)
        except ObjectDoesNotExist:
            raise ValueError(f"No {input.device_type} device found with ID {input.id} for this user.")

        # Update common fields
        if input.name is not None:
            device.name = input.name
        if input.status is not None:
            if input.status not in ["online", "offline"]:
                raise ValueError("Status must be 'online' or 'offline'")
            device.status = input.status

        # Update subclass-specific fields
        if input.device_type == "production":
            if input.instantaneous_output_watts is not None:
                device.instantaneous_output_watts = input.instantaneous_output_watts
            device.is_solar = input.is_solar
            # warn if other subclass fields are provided
            if any([
                input.total_capacity_wh,
                input.current_level_wh,
                input.charge_discharge_rate_watts,
                input.consumption_rate_watts
            ]):
                raise ValueError("Only 'instantaneous_output_watts' is allowed for production devices.")

        elif input.device_type == "storage":
            if input.total_capacity_wh is not None:
                device.total_capacity_wh = input.total_capacity_wh
            if input.current_level_wh is not None:
                if input.current_level_wh < 0 or (input.total_capacity_wh and input.current_level_wh > input.total_capacity_wh):
                    raise ValueError("current_level_wh must be between 0 and total_capacity_wh")
                device.current_level_wh = input.current_level_wh
            if input.charge_discharge_rate_watts is not None:
                device.charge_discharge_rate_watts = input.charge_discharge_rate_watts
            if input.instantaneous_output_watts or input.consumption_rate_watts:
                raise ValueError("Invalid fields for a storage device")

        elif input.device_type == "consumption":
            if input.consumption_rate_watts is not None:
                device.consumption_rate_watts = input.consumption_rate_watts
            if any([
                input.total_capacity_wh,
                input.current_level_wh,
                input.charge_discharge_rate_watts,
                input.instantaneous_output_watts
            ]):
                raise ValueError("Only 'consumption_rate_watts' is allowed for consumption devices.")

        device.save()
        return device
