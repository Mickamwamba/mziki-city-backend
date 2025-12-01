from django.db import models
from django.conf import settings
from music.models import Song
from distribution.models import Platform

class StreamCount(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='streams')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    date = models.DateField()

    class Meta:
        unique_together = ('song', 'platform', 'date')

    def __str__(self):
        return f"{self.song.title} - {self.platform.name}: {self.count}"

class Revenue(models.Model):
    song = models.ForeignKey('music.Song', on_delete=models.CASCADE, related_name='revenue')
    platform = models.ForeignKey('distribution.Platform', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        unique_together = ('song', 'platform', 'date')

    def __str__(self):
        return f"{self.song.title} - {self.platform.name} - ${self.amount}"

class PaymentProvider(models.Model):
    PROVIDER_TYPES = [
        ('BANK', 'Bank'),
        ('MOBILE', 'Mobile Money'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

from django.contrib.auth import get_user_model

User = get_user_model()

class UserPayoutMethod(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payout_method')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.SET_NULL, null=True)
    account_number = models.CharField(max_length=50) # Bank Account or Phone Number
    account_name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.artist_name} - {self.provider.name}"

class WithdrawalRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending') # pending, approved, rejected
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Link to the method used for this specific request
    payout_method_snapshot = models.TextField(null=True, blank=True) # Store details at time of request

    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"
