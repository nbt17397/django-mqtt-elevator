from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import uuid
from django.utils import timezone

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

class BoardType(ItemBase):
    class Meta:
        unique_together = ('name',)
    
    code = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)

class Location(ItemBase):
    class Meta:
        unique_together = ('name',)
    
    description = models.CharField(max_length=1000, null=True, blank=True)
    lat = models.FloatField()
    lng = models.FloatField()
    authorized_users = models.ManyToManyField(User, related_name='accessible_locations')

class Board(ItemBase):

    device_id = models.UUIDField(default=uuid.uuid4, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='boards')
    board_type = models.ForeignKey(BoardType, on_delete=models.SET_NULL, null=True, related_name='boards')
    status = models.BooleanField(default=False)
    authorized_users = models.ManyToManyField(User, related_name='accessible_boards')
    capacity = models.FloatField(null=True, blank=True)

class Group(models.Model):
    name = models.CharField(max_length=150, null=False)
    description = models.TextField(null=True, blank=True)
    
    board = models.ForeignKey('Board', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups')

    def __str__(self):
        return self.name


class BoardControlRequest(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='control_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_control_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def has_expired(self):
        return timezone.now() > self.expires_at


class Register(ItemBase):
        
    description = models.CharField(max_length=1000, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='registers')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='registers')
    value = models.IntegerField() 
    type = models.CharField(max_length=255)
    topic = models.CharField(max_length=255, null=True, blank=True) 
    status = models.BooleanField(default=True)



class Notification(models.Model): 
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='notifications') 
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=1000) 
    timestamp = models.DateTimeField(auto_now_add=True)


class HistoricalData(models.Model): 
    
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='historical_data') 
    type = models.CharField(max_length=255) 
    value = models.FloatField() 
    timestamp = models.DateTimeField(auto_now_add=True)

class HistoricalControl(models.Model): 
    
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='historical_controls') 
    type = models.CharField(max_length=255) 
    value = models.FloatField() 
    timestamp = models.DateTimeField(auto_now_add=True) 
    description = models.CharField(max_length=1000)

class RegisterSetting(models.Model): 
    
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='register_settings') 
    type = models.CharField(max_length=255) 
    value = models.FloatField() 
    timestamp = models.DateTimeField(auto_now_add=True)

class MaintenanceRecord(models.Model): 
    
    name = models.CharField(max_length=255) 
    description = models.CharField(max_length=1000, null=True, blank=True) 
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='maintenance_records') 
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='maintenance_records') 
    timestamp = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    tag_code = models.CharField(max_length=50, unique=True, null=False)
    tag_name = models.CharField(max_length=150, null=False)
    description = models.TextField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    min_value = models.IntegerField(null=True, blank=True)
    default_value = models.IntegerField(null=True, blank=True)


    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.tag_name



