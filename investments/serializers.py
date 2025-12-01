from rest_framework import serializers
from .models import InvestmentProduct, UserSubscription

class InvestmentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentProduct
        fields = '__all__'

from django.db.models import Sum
from distribution.models import RevenueSplit
from analytics.models import Revenue

class UserSubscriptionSerializer(serializers.ModelSerializer):
    product_details = InvestmentProductSerializer(source='product', read_only=True)
    total_invested = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'product', 'product_details', 'percentage', 'is_active', 'created_at', 'total_invested']
        read_only_fields = ('user', 'created_at')

    def get_total_invested(self, obj):
        total = 0
        # Find splits for this product name belonging to this user
        # Note: Matching by name is a bit fragile but consistent with current implementation
        product_name = obj.product.name
        
        # 1. Song-level splits
        song_splits = RevenueSplit.objects.filter(
            recipient=product_name, 
            song__artist=obj.user
        )
        for split in song_splits:
            revenue = Revenue.objects.filter(song=split.song).aggregate(Sum('amount'))['amount__sum'] or 0
            total += float(revenue) * (float(split.percentage) / 100)

        # 2. Album-level splits
        album_splits = RevenueSplit.objects.filter(
            recipient=product_name, 
            album__artist=obj.user
        )
        for split in album_splits:
            # Revenue for all songs in the album
            revenue = Revenue.objects.filter(song__album=split.album).aggregate(Sum('amount'))['amount__sum'] or 0
            total += float(revenue) * (float(split.percentage) / 100)
            
        return round(total, 2)
