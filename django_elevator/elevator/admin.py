from django.contrib import admin
from .models import User, Location, Board, BoardControlRequest, Register, Notification, HistoricalData, HistoricalControl, RegisterSetting, MaintenanceRecord, Tag, BoardType

admin.site.register(User)
admin.site.register(Location)
admin.site.register(Board)
admin.site.register(BoardType)
admin.site.register(BoardControlRequest)
admin.site.register(Register)
admin.site.register(Notification)
admin.site.register(HistoricalData)
admin.site.register(HistoricalControl)
admin.site.register(RegisterSetting)
admin.site.register(MaintenanceRecord)
admin.site.register(Tag)
