from django.db import models
from django.contrib.auth.models import User

class UploadHistory(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    total_count = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at}"

class Equipment(models.Model):
    upload_history = models.ForeignKey(UploadHistory, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    def __str__(self):
        return self.equipment_name
