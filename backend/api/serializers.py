from rest_framework import serializers
from .models import Equipment, UploadHistory
from django.contrib.auth.models import User

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']

class UploadHistorySerializer(serializers.ModelSerializer):
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadHistory
        fields = ['id', 'uploaded_at', 'filename', 'total_count', 'avg_flowrate', 
                  'avg_pressure', 'avg_temperature', 'equipment_count']
    
    def get_equipment_count(self, obj):
        return obj.equipment.count()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
