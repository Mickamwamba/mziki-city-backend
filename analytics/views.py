from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from .models import StreamCount, Revenue
from .serializers import StreamCountSerializer, RevenueSerializer

class AnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Aggregate total streams and revenue for the user's songs
        total_streams = StreamCount.objects.filter(song__artist=user).aggregate(Sum('count'))['count__sum'] or 0
        total_revenue = Revenue.objects.filter(song__artist=user).aggregate(Sum('amount'))['amount__sum'] or 0.0

        # Get recent data
        recent_streams = StreamCount.objects.filter(song__artist=user).order_by('-date')[:10]
        recent_revenue = Revenue.objects.filter(song__artist=user).order_by('-date')[:10]

        # Aggregate by platform
        platform_streams = StreamCount.objects.filter(song__artist=user).values('platform__name').annotate(total=Sum('count'))
        platform_revenue = Revenue.objects.filter(song__artist=user).values('platform__name').annotate(total=Sum('amount'))

        return Response({
            "total_streams": total_streams,
            "total_revenue": total_revenue,
            "recent_streams": StreamCountSerializer(recent_streams, many=True).data,
            "recent_revenue": RevenueSerializer(recent_revenue, many=True).data,
            "platform_streams": platform_streams,
            "platform_revenue": platform_revenue
        })

class SongAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, song_id):
        try:
            # Ensure user owns the song
            from music.models import Song
            song = Song.objects.get(id=song_id, artist=request.user)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

        # Aggregate total streams and revenue for this song
        total_streams = StreamCount.objects.filter(song=song).aggregate(Sum('count'))['count__sum'] or 0
        total_revenue = Revenue.objects.filter(song=song).aggregate(Sum('amount'))['amount__sum'] or 0.0

        # Get per-platform breakdown
        platform_streams = StreamCount.objects.filter(song=song).values('platform__name').annotate(total=Sum('count'))
        platform_revenue = Revenue.objects.filter(song=song).values('platform__name').annotate(total=Sum('amount'))

        return Response({
            "total_streams": total_streams,
            "total_revenue": total_revenue,
            "platform_streams": platform_streams,
            "platform_revenue": platform_revenue
        })

class WalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Calculate balance
        total_revenue = Revenue.objects.filter(song__artist=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.0
        from .models import WithdrawalRequest
        total_withdrawn = WithdrawalRequest.objects.filter(
            user=request.user, 
            status__in=['pending', 'approved']
        ).aggregate(Sum('amount'))['amount__sum'] or 0.0
        
        balance = float(total_revenue) - float(total_withdrawn)

        # Get history
        withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-requested_at')
        
        return Response({
            "balance": balance,
            "total_revenue": total_revenue,
            "withdrawals": list(withdrawals.values('id', 'amount', 'status', 'requested_at'))
        })

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=400)

        # Check balance
        total_revenue = Revenue.objects.filter(song__artist=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.0
        from .models import WithdrawalRequest
        total_withdrawn = WithdrawalRequest.objects.filter(
            user=request.user, 
            status__in=['pending', 'approved']
        ).aggregate(Sum('amount'))['amount__sum'] or 0.0
        
        balance = float(total_revenue) - float(total_withdrawn)

        if amount > balance:
            return Response({"error": "Insufficient funds"}, status=400)

        if amount <= 0:
             return Response({"error": "Amount must be positive"}, status=400)

        if amount < 50:
             return Response({"error": "Minimum withdrawal amount is $50"}, status=400)

        withdrawal = WithdrawalRequest.objects.create(
            user=request.user,
            amount=amount
        )
        
        return Response({
            "message": "Withdrawal requested",
            "balance": balance - amount,
            "withdrawal": {
                "id": withdrawal.id,
                "amount": withdrawal.amount,
                "status": withdrawal.status,
                "requested_at": withdrawal.requested_at
            }
        })

from rest_framework import viewsets
from .models import PaymentProvider, UserPayoutMethod
from .serializers import PaymentProviderSerializer, UserPayoutMethodSerializer

class PaymentProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentProvider.objects.filter(is_active=True)
    serializer_class = PaymentProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserPayoutMethodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            method = UserPayoutMethod.objects.get(user=request.user)
            return Response(UserPayoutMethodSerializer(method).data)
        except UserPayoutMethod.DoesNotExist:
            return Response(None) # Return null if not set

    def post(self, request):
        # Create or Update
        data = request.data
        try:
            method = UserPayoutMethod.objects.get(user=request.user)
            serializer = UserPayoutMethodSerializer(method, data=data, partial=True)
        except UserPayoutMethod.DoesNotExist:
            serializer = UserPayoutMethodSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
