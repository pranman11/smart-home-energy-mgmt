from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS_CHOICES = [
    ("online", "Online"),
    ("offline", "Offline"),
]

class Device(models.Model):
    """
    Abstract base model for all device types.
    """
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)ss")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.__class__.__name__})"

class StorageDevice(Device):
    """
    Represents a device that can store energy (e.g., Battery, Electric Vehicle).
    """
    total_capacity_wh = models.PositiveIntegerField(help_text="Max energy capacity in Wh")
    current_level_wh = models.PositiveIntegerField(help_text="Current charge level in Wh", default=0)
    charge_discharge_rate_watts = models.IntegerField(
        help_text="Current rate (W). Positive if charging, negative if discharging",
        default=0
    )

class ProductionDevice(Device):
    """
    Represents a device that produces energy (e.g., Solar Panel, Generator).
    """
    instantaneous_output_watts = models.PositiveIntegerField(
        help_text="Current energy production rate in watts"
    )
    is_solar = models.BooleanField(
        help_text="True if it's a solar panel"
    )

class ConsumptionDevice(Device):
    """
    Represents a device that consumes energy (e.g., AC, Heater, EV).
    """
    consumption_rate_watts = models.PositiveIntegerField(
        help_text="Current consumption rate in watts"
    )
