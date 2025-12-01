from django.contrib import admin
from users.admin import CustomUserAdmin
from music.admin import SongAdmin, AlbumAdmin
from distribution.admin import RevenueSplitAdmin, DistributionRequest
from analytics.admin import WithdrawalRequestAdmin
from .models import (
    Artist, ArtistSong, ArtistAlbum, ArtistRevenueSplit,
    ReleaseRequest, PayoutRequest, PlatformSettings, SystemUser
)
from music.models import Song, Album

# 1. Artist Management
@admin.register(Artist)
class ArtistAdmin(CustomUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_artist=True)

from django.db.models import Sum

class RevenueSplitInline(admin.TabularInline):
    model = ArtistRevenueSplit
    extra = 0
    readonly_fields = ('recipient', 'role', 'percentage')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ArtistSong)
class ArtistSongAdmin(SongAdmin):
    readonly_fields = [field.name for field in Song._meta.fields] + ['total_streams', 'total_revenue']
    list_display = ('title', 'artist', 'album', 'total_streams', 'total_revenue', 'is_released')
    inlines = [RevenueSplitInline]
    
    fieldsets = (
        ('Song Details', {
            'fields': ('title', 'version', 'artist', 'album', 'genre', 'subgenre', 'language', 'duration', 'explicit_content', 'audio_file', 'cover_art', 'created_at')
        }),
        ('Release Information', {
            'fields': ('is_released', 'release_date', 'label_name', 'catalog_number', 'excluded_countries')
        }),
        ('Credits', {
            'fields': ('primary_artist_name', 'featured_artists', 'producer', 'song_writer')
        }),
        ('Rights & Copyright', {
            'fields': ('composition_owner', 'composition_year', 'master_recording_owner', 'master_recording_year')
        }),
        ('Analytics (Read-Only)', {
            'fields': ('total_streams', 'total_revenue')
        })
    )

    def total_streams(self, obj):
        return obj.streams.aggregate(total=Sum('count'))['total'] or 0
    total_streams.short_description = "Total Streams"

    def total_revenue(self, obj):
        return f"${obj.revenue.aggregate(total=Sum('amount'))['total'] or 0:.2f}"
    total_revenue.short_description = "Total Revenue"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ArtistAlbum)
class ArtistAlbumAdmin(AlbumAdmin):
    readonly_fields = [field.name for field in Album._meta.fields] + ['total_streams', 'total_revenue']
    list_display = ('title', 'artist', 'release_date', 'total_streams', 'total_revenue', 'is_released')
    inlines = [RevenueSplitInline]

    fieldsets = (
        ('Album Details', {
            'fields': ('title', 'artist', 'genre', 'cover_art', 'created_at')
        }),
        ('Release Information', {
            'fields': ('is_released', 'release_date', 'label_name', 'upc')
        }),
        ('Analytics (Read-Only)', {
            'fields': ('total_streams', 'total_revenue')
        })
    )

    def total_streams(self, obj):
        # Sum streams for all songs in the album
        return obj.songs.aggregate(total=Sum('streams__count'))['total'] or 0
    total_streams.short_description = "Total Streams"

    def total_revenue(self, obj):
        # Sum revenue for all songs in the album
        return f"${obj.songs.aggregate(total=Sum('revenue__amount'))['total'] or 0:.2f}"
    total_revenue.short_description = "Total Revenue"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# 2. Release Management
class DistributionRequestInline(admin.TabularInline):
    model = DistributionRequest
    extra = 0
    readonly_fields = ('platform', 'status', 'distributed_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ReleaseRequest)
class ReleaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_status', 'platform_count', 'overall_status', 'created_at')
    list_filter = ('release_status', 'is_released', 'artist')
    search_fields = ('title', 'artist__artist_name', 'artist__username')
    readonly_fields = [field.name for field in Song._meta.fields]
    inlines = [DistributionRequestInline, RevenueSplitInline]
    
    fieldsets = (
        ('Release Details', {
            'fields': ('title', 'version', 'artist', 'album', 'genre', 'subgenre', 'language', 'duration', 'explicit_content', 'release_status')
        }),
        ('Release Metadata', {
            'fields': ('is_released', 'release_date', 'label_name', 'catalog_number', 'excluded_countries')
        }),
        ('Assets', {
            'fields': ('audio_file', 'cover_art')
        })
    )
    
    def get_queryset(self, request):
        # Only show songs that have at least one distribution request
        return super().get_queryset(request).filter(distributions__isnull=False).distinct()

    def platform_count(self, obj):
        return obj.distributions.count()
    platform_count.short_description = "Platforms"

    def overall_status(self, obj):
        statuses = list(obj.distributions.values_list('status', flat=True))
        if not statuses:
            return "No Requests"
        if all(s == 'distributed' for s in statuses):
            return "Distributed"
        if 'failed' in statuses:
            return "Has Failures"
        return "Pending"
    overall_status.short_description = "Platform Status"

    actions = ['approve_release', 'reject_release', 'mark_all_distributed']

    def approve_release(self, request, queryset):
        queryset.update(release_status='approved')
    approve_release.short_description = "Approve selected releases"

    def reject_release(self, request, queryset):
        queryset.update(release_status='rejected')
    reject_release.short_description = "Reject selected releases"

    def mark_all_distributed(self, request, queryset):
        from django.utils import timezone
        # Update all distribution requests for selected songs
        for song in queryset:
            song.distributions.update(status='distributed', distributed_at=timezone.now())
            song.is_released = True
            song.release_status = 'released'
            song.save()
    mark_all_distributed.short_description = "Mark as Released (Distribute All)"

    change_form_template = 'admin/admin_dashboard/releaserequest/change_form.html'

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            obj.release_status = 'approved'
            obj.save()
            self.message_user(request, "Release approved successfully.")
            return self.response_post_save_change(request, obj)
        
        if "_reject" in request.POST:
            obj.release_status = 'rejected'
            obj.save()
            self.message_user(request, "Release rejected.")
            return self.response_post_save_change(request, obj)

        if "_distribute" in request.POST:
            from django.utils import timezone
            obj.distributions.update(status='distributed', distributed_at=timezone.now())
            obj.is_released = True
            obj.release_status = 'released'
            obj.save()
            self.message_user(request, "Release distributed and marked as live.")
            return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow change so we can use the buttons, but fields are readonly
        return True

# 3. Finance
@admin.register(PayoutRequest)
class PayoutRequestAdmin(WithdrawalRequestAdmin):
    pass

# 4. Platform Management
@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url')
    search_fields = ('name',)

# 5. User Management
@admin.register(SystemUser)
class SystemUserAdmin(CustomUserAdmin):
    pass
