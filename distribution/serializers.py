from rest_framework import serializers
from .models import Platform, DistributionRequest, RevenueSplit

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'

class RevenueSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSplit
        fields = ['id', 'song', 'album', 'recipient', 'role', 'percentage']

class DistributionRequestSerializer(serializers.ModelSerializer):
    platform_details = PlatformSerializer(source='platform', read_only=True)
    
    class Meta:
        model = DistributionRequest
        fields = ['id', 'song', 'platform', 'platform_details', 'status', 'distributed_at', 'external_id']
