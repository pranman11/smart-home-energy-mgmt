from django.contrib import admin
from .models import ProductionDevice, StorageDevice, ConsumptionDevice

class BaseRestrictedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj is None or obj.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request)

@admin.register(ProductionDevice)
class ProductionDeviceAdmin(BaseRestrictedAdmin):
    list_display = (
        "name", 
        "status",
        "user", 
        "instantaneous_output_watts", 
        "updated_at"
    )
    list_filter = ("status",)
    search_fields = ("name", "user__username")


@admin.register(StorageDevice)
class StorageDeviceAdmin(BaseRestrictedAdmin):
    list_display = (
        "name",
        "status",
        "user",
        "total_capacity_wh",
        "current_level_wh",
        "charge_discharge_rate_watts",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("name", "user__username")


@admin.register(ConsumptionDevice)
class ConsumptionDeviceAdmin(BaseRestrictedAdmin):
    list_display = (
        "name", 
        "status", 
        "user", 
        "consumption_rate_watts", 
        "updated_at"
    )
    list_filter = ("status",)
    search_fields = ("name", "user__username")
