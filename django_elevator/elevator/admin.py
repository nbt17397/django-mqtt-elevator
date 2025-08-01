from django.contrib import admin
from .models import (
    User, Location, LocationUser, System, Pond, AnimalType, Unit, FeedingMenuItem, 
    FeedingMenu, FoodType, FarmingCycle, FarmingCyclePond, Task, 
    DensityRecord, HealthRecord, WaterQualityRecord, Product, Inventory, StockTransaction, StockTransactionDetail, Alert,
    Device, DeviceGroup, DeviceFunctionGroup, DeviceSetting, DeviceDataLog
)
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Location, SimpleHistoryAdmin)
admin.site.register(LocationUser)
admin.site.register(System)
admin.site.register(Pond)
admin.site.register(AnimalType)
admin.site.register(Unit)
admin.site.register(FoodType)
admin.site.register(FeedingMenu)
admin.site.register(FeedingMenuItem)
admin.site.register(FarmingCycle)
admin.site.register(FarmingCyclePond)
admin.site.register(Task)

# Đăng ký các model mới
admin.site.register(DensityRecord)
admin.site.register(HealthRecord)
admin.site.register(WaterQualityRecord)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(StockTransaction)
admin.site.register(StockTransactionDetail)
admin.site.register(Alert)
admin.site.register(Device)
admin.site.register(DeviceGroup)
admin.site.register(DeviceFunctionGroup)
admin.site.register(DeviceSetting)
admin.site.register(DeviceDataLog)
