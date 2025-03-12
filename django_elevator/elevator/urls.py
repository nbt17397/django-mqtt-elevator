from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'boards', views.BoardViewSet)
router.register(r'board_types', views.BoardTypeViewSet)
router.register(r'registers', views.RegisterViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'historical_data', views.HistoricalDataViewSet)
router.register(r'historical_controls', views.HistoricalControlViewSet)
router.register(r'register_settings', views.RegisterSettingViewSet)
router.register(r'maintenance_records', views.MaintenanceRecordViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/login/', views.login_api),
    path('api/user/', views.get_user_data),
    path('api/receive-data/', views.receive_data),
    path('api/notification-data/',views.notification_data)
]