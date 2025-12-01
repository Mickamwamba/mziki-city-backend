from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlatformViewSet, DistributionRequestViewSet, RevenueSplitViewSet

router = DefaultRouter()
router.register(r'platforms', PlatformViewSet)
router.register(r'requests', DistributionRequestViewSet, basename='distribution-requests')
router.register(r'splits', RevenueSplitViewSet, basename='revenue-splits')

urlpatterns = [
    path('', include(router.urls)),
]
