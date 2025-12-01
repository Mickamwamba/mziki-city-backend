from rest_framework import serializers
from .models import StreamCount, Revenue

class StreamCountSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    song_title = serializers.CharField(source='song.title', read_only=True)

    class Meta:
        model = StreamCount
        fields = '__all__'

class RevenueSerializer(serializers.ModelSerializer):
    song_title = serializers.CharField(source='song.title', read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    
    class Meta:
        model = Revenue
        fields = ['id', 'song', 'song_title', 'platform', 'platform_name', 'amount', 'date']

from .models import PaymentProvider, UserPayoutMethod

class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = '__all__'

class UserPayoutMethodSerializer(serializers.ModelSerializer):
    provider_details = PaymentProviderSerializer(source='provider', read_only=True)
    
    class Meta:
        model = UserPayoutMethod
        fields = ['id', 'provider', 'provider_details', 'account_number', 'account_name', 'updated_at']
