from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import  User, Location, Board, Register, Notification, HistoricalData, HistoricalControl, RegisterSetting, MaintenanceRecord
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
    

class LocationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class LocationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'description', 'lat', 'lng', 'authorized_users']

class BoardReadSerializer(serializers.ModelSerializer):
    location = LocationReadSerializer(read_only=True)
    authorized_users = UserReadSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = '__all__'

class BoardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'description', 'location', 'status', 'device_id', 'authorized_users']


class RegisterReadSerializer(serializers.ModelSerializer):
    board = BoardReadSerializer(read_only=True)

    class Meta:
        model = Register
        fields = '__all__'

class RegisterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['name', 'description', 'board', 'value', 'type', 'status']


class NotificationReadSerializer(serializers.ModelSerializer):
    board = BoardReadSerializer(read_only=True)
    register = RegisterReadSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'

class NotificationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'board', 'register', 'description']


class HistoricalDataReadSerializer(serializers.ModelSerializer):
    register = RegisterReadSerializer(read_only=True)

    class Meta:
        model = HistoricalData
        fields = '__all__'

class HistoricalDataWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalData
        fields = ['register', 'type', 'value', 'timestamp']


class HistoricalControlReadSerializer(serializers.ModelSerializer):
    register = RegisterReadSerializer(read_only=True)

    class Meta:
        model = HistoricalControl
        fields = '__all__'

class HistoricalControlWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalControl
        fields = ['register', 'type', 'value', 'timestamp', 'description']


class RegisterSettingReadSerializer(serializers.ModelSerializer):
    register = RegisterReadSerializer(read_only=True)

    class Meta:
        model = RegisterSetting
        fields = '__all__'

class RegisterSettingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterSetting
        fields = ['register', 'type', 'value', 'timestamp']


class MaintenanceRecordReadSerializer(serializers.ModelSerializer):
    register = RegisterReadSerializer(read_only=True)
    board = BoardReadSerializer(read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'

class MaintenanceRecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = ['name', 'description', 'register', 'board', 'timestamp']






