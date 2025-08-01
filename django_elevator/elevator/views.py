from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone

from .models import (
    User, Location, System, Pond, AnimalType, Unit,
    FoodType, FeedingMenu, FeedingMenuItem,
    FarmingCycle, FarmingCyclePond, Task,
    WaterQualityRecord, DensityRecord, HealthRecord,
    Product, Inventory, StockTransaction, StockTransactionDetail,
    Alert, DeviceGroup, DeviceFunctionGroup, Device,
    DeviceSetting, DeviceDataLog
)
from .serializers import (
    UserSerializer, UserReadSerializer,
    LocationSerializer, LocationWriteSerializer,
    SystemSerializer, SystemReadSerializer,
    PondSerializer, PondReadSerializer,
    AnimalTypeSerializer, UnitSerializer,
    FoodTypeSerializer,
    FeedingMenuWriteSerializer, FeedingMenuReadSerializer,
    FeedingMenuItemWriteSerializer, FeedingMenuItemReadSerializer,
    FarmingCycleWriteSerializer, FarmingCycleReadSerializer,
    FarmingCycleNestedSerializer,
    FarmingCyclePondWriteSerializer, FarmingCyclePondReadSerializer,
    TaskWriteSerializer, TaskReadSerializer,
    DensityRecordSerializer, HealthRecordSerializer,
    WaterQualityRecordSerializer,
    ProductSerializer, InventorySerializer,
    StockTransactionSerializer, StockTransactionDetailSerializer,
    AlertSerializer,
    DeviceGroupSerializer, DeviceFunctionGroupSerializer,
    DeviceSerializer, DeviceSettingSerializer,
    DeviceDataLogSerializer
)
from .paginator import StandardResultsSetPagination, LargeResultsSetPagination


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    user.auth_token_set.all().delete()
    _, token = AuthToken.objects.create(user)

    device_token = request.data.get('device_token')
    if device_token is not None:
        user.device_token = device_token
        user.save()

    return Response({
        'user_info': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'device_token': user.device_token,
            'name': user.name,
            'is_superuser': user.is_superuser,
        },
        'token': token
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_data(request):
    user = request.user
    return Response({'user_info': {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }})


class UserViewSet(viewsets.GenericViewSet,
                  generics.ListAPIView,
                  generics.CreateAPIView,
                  generics.RetrieveAPIView,
                  generics.UpdateAPIView,
                  generics.DestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='current-user')
    def current_user(self, request):
        return Response(UserReadSerializer(request.user).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LocationSerializer
        return LocationWriteSerializer


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PondViewSet(viewsets.ModelViewSet):
    queryset = Pond.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PondReadSerializer
        return PondSerializer


class AnimalTypeViewSet(viewsets.ModelViewSet):
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]


class FoodTypeViewSet(viewsets.ModelViewSet):
    queryset = FoodType.objects.all()
    serializer_class = FoodTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedingMenuViewSet(viewsets.ModelViewSet):
    queryset = FeedingMenu.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FeedingMenuReadSerializer
        return FeedingMenuWriteSerializer


class FeedingMenuItemViewSet(viewsets.ModelViewSet):
    queryset = FeedingMenuItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FeedingMenuItemReadSerializer
        return FeedingMenuItemWriteSerializer


class FarmingCycleViewSet(viewsets.ModelViewSet):
    queryset = FarmingCycle.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FarmingCycleReadSerializer
        return FarmingCycleWriteSerializer


class FarmingCyclePondViewSet(viewsets.ModelViewSet):
    queryset = FarmingCyclePond.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FarmingCyclePondReadSerializer
        return FarmingCyclePondWriteSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer
        return TaskWriteSerializer


# Data Records
class DensityRecordViewSet(viewsets.ModelViewSet):
    queryset = DensityRecord.objects.all()
    serializer_class = DensityRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


class WaterQualityRecordViewSet(viewsets.ModelViewSet):
    queryset = WaterQualityRecord.objects.all()
    serializer_class = WaterQualityRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


# Inventory & Stock
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]


class StockTransactionViewSet(viewsets.ModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


class StockTransactionDetailViewSet(viewsets.ModelViewSet):
    queryset = StockTransactionDetail.objects.all()
    serializer_class = StockTransactionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


# Alerts and Devices
class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceFunctionGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceFunctionGroup.objects.all()
    serializer_class = DeviceFunctionGroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceSettingViewSet(viewsets.ModelViewSet):
    queryset = DeviceSetting.objects.all()
    serializer_class = DeviceSettingSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceDataLogViewSet(viewsets.ModelViewSet):
    queryset = DeviceDataLog.objects.all()
    serializer_class = DeviceDataLogSerializer
    permission_classes = [permissions.IsAuthenticated]
