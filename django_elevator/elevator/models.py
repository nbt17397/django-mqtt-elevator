from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import uuid
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.core.validators import FileExtensionValidator

class User(AbstractUser):

    name = models.CharField(max_length=150, null=False)
    device_token = models.CharField(max_length=50, null=True, blank=True)


class ItemBase(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=150, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Location(ItemBase):
    class Meta:
        unique_together = ('name',)
    
    description = models.CharField(max_length=1000, null=True, blank=True)
    lat = models.FloatField()
    lng = models.FloatField()
    authorized_users = models.ManyToManyField(
        User,
        through='LocationUser',
        related_name='accessible_locations'
    )

class LocationUser(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('operator', 'Operator'),
    )

    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('location', 'user')

class System(models.Model):

    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='systems')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    
class Pond(models.Model):
    system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='ponds')
    name = models.CharField(max_length=255)
    volume = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    

class AnimalType(models.Model):
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='animal_types'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'animal_types'
        ordering = ['name']


class Unit(models.Model):
    TYPE_CHOICES = (
        ('mass', 'Khối lượng'),     # gram, kg
        ('volume', 'Thể tích'),     # lít, m³
        ('count', 'Số lượng'),      # con, cái
        ('custom', 'Khác')
    )

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default='pond'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='units'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'units'
        ordering = ['name']


class FeedingMenu(models.Model):
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='feeding_menus'
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'feeding_menus'
        ordering = ['name']


class FoodType(models.Model):
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='food_types'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'food_types'
        ordering = ['name']


class FeedingMenuItem(models.Model):
    feeding_menu = models.ForeignKey(
        FeedingMenu,
        on_delete=models.CASCADE,
        related_name='items'
    )
    food_type = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='feeding_menu_items',
        null=True, blank=True
    )
    ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Tỷ lệ phần trăm, ví dụ 25.50'
    )

    def __str__(self):
        return f"{self.food_type.name} in {self.feeding_menu.name} ({self.ratio}%)"

    class Meta:
        db_table = 'feeding_menu_items'
        unique_together = ('feeding_menu', 'food_type')
        ordering = ['feeding_menu']


class FarmingCycle(models.Model):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='farming_cycles'
    )
    animal_type = models.ForeignKey(
        'AnimalType',
        on_delete=models.CASCADE,
        related_name='farming_cycles'
    )
    cycle_code = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    initial_quantity = models.IntegerField()
    remaining_quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.cycle_code} ({self.get_status_display()})"

    class Meta:
        db_table = 'farming_cycles'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['cycle_code']),
            models.Index(fields=['status']),
        ]

class FarmingCyclePond(models.Model):
    farming_cycle = models.ForeignKey(
        FarmingCycle,
        on_delete=models.CASCADE,
        related_name='cycle_pond_links'
    )
    pond = models.ForeignKey(
        Pond,
        on_delete=models.CASCADE,
        related_name='cycle_pond_links'
    )
    initial_quantity = models.IntegerField(
        help_text='Số lượng thả ở bể này khi bắt đầu vụ'
    )
    remaining_quantity = models.IntegerField(
        help_text='Số lượng còn lại ở bể này hiện tại'
    )

    class Meta:
        db_table = 'farming_cycle_ponds'
        unique_together = ('farming_cycle', 'pond')


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    pond = models.ForeignKey(
        'Pond',
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    farming_cycle = models.ForeignKey(
        'FarmingCycle',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text='Người được giao nhiệm vụ'
    )

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    class Meta:
        db_table = 'tasks'
        ordering = ['-start_datetime']


class DensityRecord(models.Model):
    farming_cycle = models.ForeignKey(
        'FarmingCycle',
        on_delete=models.CASCADE,
        related_name='density_records'
    )
    pond = models.ForeignKey(
        'Pond',
        on_delete=models.CASCADE,
        related_name='density_records'
    )
    record_date = models.DateField()
    quantity = models.IntegerField()
    density = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pond} - {self.record_date}: {self.quantity} con"

    class Meta:
        db_table = 'density_records'
        unique_together = ('farming_cycle', 'pond', 'record_date')
        ordering = ['-record_date']


class WaterQualityRecord(models.Model):
    farming_cycle = models.ForeignKey(
        'FarmingCycle',
        on_delete=models.CASCADE,
        related_name='water_quality_records'
    )
    pond = models.ForeignKey(
        'Pond',
        on_delete=models.CASCADE,
        related_name='water_quality_records'
    )
    record_date = models.DateField()
    discharge_volume = models.DecimalField(  # khối lượng xả (m3)
        max_digits=10,
        decimal_places=2
    )
    pump_volume = models.DecimalField(       # khối lượng bơm vào (m3)
        max_digits=10,
        decimal_places=2
    )
    image_url = models.ImageField(
        upload_to='water_quality_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text='Ảnh minh hoạ'
    )
    pH = models.DecimalField(                # độ pH
        max_digits=4,
        decimal_places=2
    )
    dissolved_oxygen = models.DecimalField(  # oxy hoà tan
        max_digits=5,
        decimal_places=2
    )
    evaluation = models.IntegerField(        # từ -2 đến 2
        help_text='Đánh giá chất lượng (-2: rất xấu → 2: rất tốt)'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pond} - {self.record_date} - pH: {self.pH}"

    class Meta:
        db_table = 'water_quality_records'
        unique_together = ('farming_cycle', 'pond', 'record_date')
        ordering = ['-record_date']


class HealthRecord(models.Model):
    farming_cycle = models.ForeignKey(
        'FarmingCycle',
        on_delete=models.CASCADE,
        related_name='health_records'
    )
    pond = models.ForeignKey(
        'Pond',
        on_delete=models.CASCADE,
        related_name='health_records'
    )
    record_date = models.DateField()
    length_cm = models.DecimalField(max_digits=6, decimal_places=2)
    width_cm = models.DecimalField(max_digits=6, decimal_places=2)
    health_status = models.IntegerField(
        help_text='Tình trạng sức khoẻ (-2 đến 2)'
    )
    feces_status = models.IntegerField(
        help_text='Tình trạng phân (-2 đến 2)'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pond} - {self.record_date} - Health: {self.health_status}"

    class Meta:
        db_table = 'health_records'
        unique_together = ('farming_cycle', 'pond', 'record_date')
        ordering = ['-record_date']

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('feed', 'Thức ăn'),
        ('equipment', 'Thiết bị'),
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES)
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
        ordering = ['name']


class Inventory(models.Model):
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='inventories'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='inventories'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventories'
        unique_together = ('location', 'product')


class StockTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('import', 'Nhập kho'),
        ('export', 'Xuất kho'),
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='stock_transactions'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='stock_transactions'
    )
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'stock_transactions'
        ordering = ['-created_at']


class StockTransactionDetail(models.Model):
    stock_transaction = models.ForeignKey(
        'StockTransaction',
        on_delete=models.CASCADE,
        related_name='details'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='transaction_details'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'stock_transaction_details'


class Alert(models.Model):
    TYPE_CHOICES = (
        ('device', 'Device'),
        ('task', 'Task'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    severity = models.IntegerField()  # 1 - 3
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} Alert - {self.status} - Severity {self.severity}"
    

class DeviceGroup(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class DeviceFunctionGroup(models.Model):
    device_group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    mode = models.CharField(max_length=10, choices=[('auto', 'Auto'), ('manual', 'Manual')])
    created_at = models.DateTimeField(auto_now_add=True)

class Device(models.Model):
    function_group = models.ForeignKey(DeviceFunctionGroup, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class DeviceSetting(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class DeviceDataLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField()
    data = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)





