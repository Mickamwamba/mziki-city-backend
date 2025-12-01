from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentProductViewSet, UserSubscriptionViewSet

router = DefaultRouter()
router.register(r'products', InvestmentProductViewSet)
router.register(r'subscriptions', UserSubscriptionViewSet, basename='user-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
]
