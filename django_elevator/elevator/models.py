from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import uuid


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
    authorized_users = models.ManyToManyField(User, related_name='accessible_locations')

class Board(ItemBase):

    device_id = models.UUIDField(default=uuid.uuid4, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='boards')
    status = models.BooleanField(default=False)
    authorized_users = models.ManyToManyField(User, related_name='accessible_boards')


class Register(ItemBase):
        
    description = models.CharField(max_length=1000, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='registers')
    value = models.IntegerField() 
    type = models.CharField(max_length=255) 
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


