from django.db import models

class User(models.Model):
    name = models.CharField(max_length=60)

class DeviceType(models.Model):
    type = models.CharField(max_length=3, primary_key=True)
    latest_version = models.CharField(max_length=16)

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    modification = models.IntegerField(default=0)
    version = models.CharField(max_length=16)
    rotation_cycle_length = models.IntegerField(default=80)
    forced_rotation_temp = models.IntegerField(default=0)
    night_length = models.IntegerField(default=480)
    max_intake_time = models.IntegerField(default=5)
    max_exhaust_time = models.IntegerField(default=5)
    winter_rotation_count = models.IntegerField(default=45)