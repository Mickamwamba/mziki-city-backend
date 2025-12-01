from django.contrib import admin
from django.utils import timezone
from .models import StreamCount, Revenue, WithdrawalRequest, PaymentProvider, UserPayoutMethod

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)

@admin.register(UserPayoutMethod)
class UserPayoutMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'account_name', 'account_number', 'updated_at')
    search_fields = ('user__username', 'user__email', 'account_name', 'account_number')
    list_filter = ('provider__type',)

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'requested_at', 'processed_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('requested_at', 'processed_at')
    actions = ['approve_payout', 'reject_payout']

    def approve_payout(self, request, queryset):
        # Logic to approve payout
        # In a real app, this might trigger a bank API call
        queryset.update(status='approved', processed_at=timezone.now())
        # Deduct from user balance if not already done (assuming balance logic is handled elsewhere or here)
        # For now, we just update status as per request
    approve_payout.short_description = "Approve selected payout requests"

    def reject_payout(self, request, queryset):
        # Logic to reject payout
        # Should refund the amount to user balance if it was deducted on request
        queryset.update(status='rejected', processed_at=timezone.now())
    reject_payout.short_description = "Reject selected payout requests"

@admin.register(StreamCount)
class StreamCountAdmin(admin.ModelAdmin):
    list_display = ('song', 'platform', 'count', 'date')
    list_filter = ('platform', 'date')
    search_fields = ('song__title',)

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ('song', 'platform', 'amount', 'date')
    list_filter = ('platform', 'date')
    search_fields = ('song__title',)
