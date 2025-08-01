from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import  User, Location, System, Pond, AnimalType, Unit, FoodType, FeedingMenu, FeedingMenuItem, FarmingCycle, FarmingCyclePond, Task
from .models import WaterQualityRecord, DensityRecord, HealthRecord, Product, Inventory, StockTransaction,StockTransactionDetail
from .models import Alert, Device, DeviceGroup, DeviceFunctionGroup, DeviceSetting, DeviceDataLog
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "name", "email",
                  "username", "password", "date_joined", "device_token", "is_superuser"]
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
    
class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class LocationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'description', 'lat', 'lng', 'authorized_users']

class SystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = System
        fields = '__all__'

class PondSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pond
        fields = '__all__'

class PondReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pond
        fields = ['id', 'name', 'volume', 'created_at']

class SystemReadSerializer(serializers.ModelSerializer):
    ponds = PondReadSerializer(many=True, read_only=True)

    class Meta:
        model = System
        fields = ['id', 'location', 'name', 'description', 'created_at', 'ponds']

class AnimalTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnimalType
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'

class FoodTypeSerializer(serializers.ModelSerializer):
    """
    Read/Write serializer cho FoodType.
    """
    class Meta:
        model = FoodType
        fields = ['id', 'location', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class FeedingMenuItemWriteSerializer(serializers.ModelSerializer):
    """
    Write-only: chỉ chấp nhận khóa ngoại là ID và tỷ lệ.
    """
    class Meta:
        model = FeedingMenuItem
        fields = ['id', 'feeding_menu', 'food_type', 'unit', 'ratio']
        read_only_fields = ['id']


class FeedingMenuItemReadSerializer(serializers.ModelSerializer):
    """
    Read-only: hiển thị cả thông tin cơ bản của FoodType.
    """
    food_type = FoodTypeSerializer(read_only=True)

    class Meta:
        model = FeedingMenuItem
        fields = ['id', 'food_type', 'unit', 'ratio']

class FeedingMenuWriteSerializer(serializers.ModelSerializer):
    """
    Write-only: nhận location (ID) và tên menu.
    Items có thể gửi lên riêng qua endpoint items.
    """
    class Meta:
        model = FeedingMenu
        fields = ['id', 'location', 'name']
        read_only_fields = ['id']


class FeedingMenuReadSerializer(serializers.ModelSerializer):
    """
    Read-only: hiển thị chi tiết menu kèm danh sách items.
    """
    items = FeedingMenuItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = FeedingMenu
        fields = ['id', 'location', 'name', 'created_at', 'items']
        read_only_fields = ['id', 'created_at', 'items']

# 1. FarmingCyclePond
# ---------------------------

class FarmingCyclePondWriteSerializer(serializers.ModelSerializer):
    """
    Write-only serializer: chỉ cần truyền IDs và số lượng.
    """
    class Meta:
        model = FarmingCyclePond
        fields = ['farming_cycle', 'pond', 'initial_quantity', 'remaining_quantity']


class PondNestedSerializer(serializers.ModelSerializer):
    """
    Serializer read-only để hiển thị thông tin pond khi nested.
    """
    class Meta:
        model = Pond
        fields = ['id', 'name', 'volume', 'created_at']


class FarmingCyclePondReadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer: nested thông tin pond cùng với số lượng.
    """
    pond = PondNestedSerializer(read_only=True)

    class Meta:
        model = FarmingCyclePond
        fields = ['pond', 'initial_quantity', 'remaining_quantity']

# ---------------------------
# 2. FarmingCycle
# ---------------------------

class FarmingCycleWriteSerializer(serializers.ModelSerializer):
    """
    Write-only serializer cho FarmingCycle.
    Chỉ nhận các trường cơ bản (không include pond links).
    """
    class Meta:
        model = FarmingCycle
        fields = [
            'id', 'location', 'animal_type', 'cycle_code',
            'start_date', 'end_date', 'status',
            'initial_quantity', 'remaining_quantity'
        ]
        read_only_fields = ['id']


class FarmingCycleReadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer cho FarmingCycle, nested danh sách ponds.
    """
    ponds = FarmingCyclePondReadSerializer(
        source='cycle_pond_links', many=True, read_only=True
    )
    animal_type_name = serializers.CharField(
        source='animal_type.name', read_only=True
    )

    class Meta:
        model = FarmingCycle
        fields = [
            'id', 'location', 'animal_type', 'animal_type_name',
            'cycle_code', 'start_date', 'end_date', 'status',
            'initial_quantity', 'remaining_quantity',
            'created_at', 'ponds'
        ]
        read_only_fields = ['id', 'created_at', 'animal_type_name', 'ponds']


class FarmingCycleNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmingCycle
        fields = ['id', 'cycle_code']

# ---------------------------
# 1. Task Write Serializer
# ---------------------------
class TaskWriteSerializer(serializers.ModelSerializer):
    """
    Dùng cho các thao tác tạo/sửa: nhận IDs của pond và (tuỳ chọn) farming_cycle.
    """
    class Meta:
        model = Task
        fields = [
            'id', 'pond', 'farming_cycle',
            'title', 'description', 'status',
            'start_datetime', 'end_datetime',
            'completed_at'
        ]
        read_only_fields = ['id']


# ---------------------------
# 2. Task Read Serializer
# ---------------------------
class TaskReadSerializer(serializers.ModelSerializer):
    """
    Dùng để đọc: nested thông tin pond và farming_cycle, hiển thị label của status.
    """
    pond = PondNestedSerializer(read_only=True)
    farming_cycle = FarmingCycleNestedSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'pond', 'farming_cycle',
            'title', 'description', 'status', 'status_display',
            'start_datetime', 'end_datetime',
            'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'status_display'
        ]

class DensityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DensityRecord
        fields = '__all__'

class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = '__all__'
        
class WaterQualityRecordSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = WaterQualityRecord
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_url and request:
            return request.build_absolute_uri(obj.image_url.url)
        return None
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'

class StockTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransactionDetail
        fields = '__all__'

class StockTransactionSerializer(serializers.ModelSerializer):
    details = StockTransactionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = StockTransaction
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class DeviceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceGroup
        fields = '__all__'

class DeviceFunctionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFunctionGroup
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class DeviceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSetting
        fields = '__all__'

class DeviceDataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDataLog
        fields = '__all__'