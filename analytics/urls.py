from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsDashboardView, SongAnalyticsView, WalletView, PaymentProviderViewSet, UserPayoutMethodView

router = DefaultRouter()
router.register(r'payment-providers', PaymentProviderViewSet)

urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('song/<int:song_id>/', SongAnalyticsView.as_view(), name='song-analytics'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('payout-method/', UserPayoutMethodView.as_view(), name='payout-method'),
    path('', include(router.urls)),
]
