from django.contrib import admin
from .models import User, Location, Board, Register, Notification, HistoricalData, HistoricalControl, RegisterSetting, MaintenanceRecord

admin.site.register(User)
admin.site.register(Location)
admin.site.register(Board)
admin.site.register(Register)
admin.site.register(Notification)
admin.site.register(HistoricalData)
admin.site.register(HistoricalControl)
admin.site.register(RegisterSetting)
admin.site.register(MaintenanceRecord)