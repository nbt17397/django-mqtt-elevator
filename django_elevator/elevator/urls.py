from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Auth & User
router.register(r'users', views.UserViewSet, basename='user')
# Location & System
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'systems', views.SystemViewSet, basename='system')
# Pond, AnimalType, Unit
router.register(r'ponds', views.PondViewSet, basename='pond')
router.register(r'animal-types', views.AnimalTypeViewSet, basename='animaltype')
router.register(r'units', views.UnitViewSet, basename='unit')
# Food & Feeding Menus
router.register(r'food-types', views.FoodTypeViewSet, basename='foodtype')
router.register(r'feeding-menus', views.FeedingMenuViewSet, basename='feedingmenu')
router.register(r'feeding-menu-items', views.FeedingMenuItemViewSet, basename='feedingmenuitem')
# Farming Cycles
router.register(r'farming-cycles', views.FarmingCycleViewSet, basename='farmingcycle')
router.register(r'farming-cycle-ponds', views.FarmingCyclePondViewSet, basename='farmingcyclepond')
# Tasks
router.register(r'tasks', views.TaskViewSet, basename='task')
# Data Records
router.register(r'density-records', views.DensityRecordViewSet, basename='densityrecord')
router.register(r'health-records', views.HealthRecordViewSet, basename='healthrecord')
router.register(r'water-quality-records', views.WaterQualityRecordViewSet, basename='waterqualityrecord')
# Inventory & Stock
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'inventories', views.InventoryViewSet, basename='inventory')
router.register(r'stock-transactions', views.StockTransactionViewSet, basename='stocktransaction')
router.register(r'stock-transaction-details', views.StockTransactionDetailViewSet, basename='stocktransactiondetail')
# Alerts & Devices
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'device-groups', views.DeviceGroupViewSet, basename='devicegroup')
router.register(r'device-function-groups', views.DeviceFunctionGroupViewSet, basename='devicefunctiongroup')
router.register(r'devices', views.DeviceViewSet, basename='device')
router.register(r'device-settings', views.DeviceSettingViewSet, basename='devicesetting')
router.register(r'device-data-logs', views.DeviceDataLogViewSet, basename='devicedatalog')

urlpatterns = [
    path('', include(router.urls)),
    path('api/login/', views.login_api, name='login'),
    path('api/user/', views.get_user_data, name='get_user_data'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
