from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InvestmentProduct, UserSubscription
from .serializers import InvestmentProductSerializer, UserSubscriptionSerializer

class InvestmentProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvestmentProduct.objects.filter(is_active=True)
    serializer_class = InvestmentProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active subscriptions for the current user"""
        subscriptions = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
