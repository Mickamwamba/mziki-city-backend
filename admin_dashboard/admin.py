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

from distribution.models import ReleaseRequestContent, ReleaseRequestPlatform



class ReleaseRequestPlatformInline(admin.TabularInline):
    model = ReleaseRequestPlatform
    extra = 0
    readonly_fields = ('platform', 'status', 'distributed_at', 'external_id')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ReleaseRequest)
class ReleaseRequestAdmin(admin.ModelAdmin):
    list_display = ('cover_art_preview', 'title', 'artist', 'status', 'created_at')
    list_display_links = ('cover_art_preview', 'title', 'artist', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'artist__username', 'artist__email')
    inlines = [ReleaseRequestPlatformInline]
    
    readonly_fields = ('content_details',)
    fieldsets = (
        (None, {
            'fields': ('content_details',)
        }),
    )
    
    def content_details(self, obj):
        from django.utils.html import format_html, mark_safe
        
        content = obj.contents.first()
        if not content:
            return "No content details available."
            
        html = '<div style="background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">'
        
        if content.song:
            song = content.song
            # Header with Cover and Title
            html += f'''
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <img src="{song.cover_art.url if song.cover_art else ''}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: #eee;" />
                <div>
                    <h3 style="margin: 0 0 5px 0; font-size: 18px;">{song.title} <span style="font-size: 12px; color: #64748b; font-weight: normal;">(Single)</span></h3>
                    <p style="margin: 0; color: #64748b;">{song.artist.username}</p>
                    <div style="margin-top: 10px; display: flex; gap: 10px;">
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{song.genre}</span>
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{song.duration or '--:--'}</span>
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{song.get_explicit_content_display()}</span>
                    </div>
                </div>
            </div>
            '''
            
            # Grid Layout for Details
            html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">'
            
            # Left Column: Release Info & Credits
            html += '<div>'
            html += '<h4 style="border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px;">Release Info & Credits</h4>'
            html += f'<p><strong>Label:</strong> {song.label_name or "-"}</p>'
            html += f'<p><strong>Catalog #:</strong> {song.catalog_number or "-"}</p>'
            html += f'<p><strong>Release Date:</strong> {song.release_date or "-"}</p>'
            html += f'<p><strong>Primary Artist:</strong> {song.primary_artist_name}</p>'
            html += f'<p><strong>Featured:</strong> {song.featured_artists or "-"}</p>'
            html += f'<p><strong>Producer:</strong> {song.producer or "-"}</p>'
            html += f'<p><strong>Songwriter:</strong> {song.song_writer or "-"}</p>'
            html += '</div>'
            
            # Right Column: Rights & Assets
            html += '<div>'
            html += '<h4 style="border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px;">Rights & Assets</h4>'
            html += f'<p><strong>Composition:</strong> {song.composition_owner} ({song.composition_year or "-"})</p>'
            html += f'<p><strong>Master:</strong> {song.master_recording_owner} ({song.master_recording_year or "-"})</p>'
            html += f'<p style="margin-top: 10px;"><strong>Audio File:</strong> <a href="{song.audio_file.url}" target="_blank" style="color: #3b82f6;">Listen / Download</a></p>'
            html += '</div>'
            
            html += '</div>' # End Grid
            
            # Splits Section
            splits = song.revenue_splits.all()
            if splits.exists():
                html += '<div style="margin-top: 20px;">'
                html += '<h4 style="border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px;">Revenue Splits</h4>'
                html += '<table style="width: 100%; text-align: left; border-collapse: collapse;">'
                html += '<tr style="background: #f1f5f9;"><th style="padding: 8px;">Recipient</th><th style="padding: 8px;">Role</th><th style="padding: 8px;">Percentage</th></tr>'
                for split in splits:
                    html += f'<tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{split.recipient}</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{split.role}</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{split.percentage}%</td></tr>'
                html += '</table>'
                html += '</div>'

        elif content.album:
            album = content.album
            # Header
            html += f'''
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <img src="{album.cover_art.url if album.cover_art else ''}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: #eee;" />
                <div>
                    <h3 style="margin: 0 0 5px 0; font-size: 18px;">{album.title} <span style="font-size: 12px; color: #64748b; font-weight: normal;">(Album)</span></h3>
                    <p style="margin: 0; color: #64748b;">{album.artist.username}</p>
                    <div style="margin-top: 10px; display: flex; gap: 10px;">
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{album.genre}</span>
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{album.songs.count()} Tracks</span>
                    </div>
                </div>
            </div>
            '''
            
            # Info
            html += '<div style="margin-bottom: 20px;">'
            html += f'<p><strong>Label:</strong> {album.label_name or "-"}</p>'
            html += f'<p><strong>UPC:</strong> {album.upc or "-"}</p>'
            html += f'<p><strong>Release Date:</strong> {album.release_date or "-"}</p>'
            html += '</div>'
            
            # Tracks
            songs = album.songs.all()
            if songs.exists():
                html += '<div>'
                html += '<h4 style="border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px;">Tracklist</h4>'
                html += '<table style="width: 100%; text-align: left; border-collapse: collapse;">'
                html += '<tr style="background: #f1f5f9;"><th style="padding: 8px;">#</th><th style="padding: 8px;">Title</th><th style="padding: 8px;">Duration</th><th style="padding: 8px;">Audio</th></tr>'
                for i, song in enumerate(songs, 1):
                    html += f'<tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{i}</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{song.title}</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{song.duration or "-"}</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;"><a href="{song.audio_file.url}" target="_blank">Listen</a></td></tr>'
                html += '</table>'
                html += '</div>'

        html += '</div>'
        return mark_safe(html)
    content_details.short_description = "Release Content Details"
    
    def cover_art_preview(self, obj):
        from django.utils.html import format_html
        content = obj.contents.first()
        if content:
            if content.song and content.song.cover_art:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', content.song.cover_art.url)
            elif content.album and content.album.cover_art:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', content.album.cover_art.url)
        return "-"
    cover_art_preview.short_description = "Cover"
    
    actions = ['approve_releases', 'reject_releases', 'mark_released']

    def approve_releases(self, request, queryset):
        queryset.update(status='approved')
    approve_releases.short_description = "Approve selected releases"

    def reject_releases(self, request, queryset):
        queryset.update(status='rejected')
    reject_releases.short_description = "Reject selected releases"

    def mark_released(self, request, queryset):
        queryset.update(status='released')
    mark_released.short_description = "Mark selected releases as Released"

    change_form_template = 'admin/admin_dashboard/releaserequest/change_form.html'

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            obj.status = 'approved'
            obj.save()
            self.message_user(request, "Release approved successfully.")
            return self.response_post_save_change(request, obj)
        
        if "_reject" in request.POST:
            obj.status = 'rejected'
            obj.save()
            self.message_user(request, "Release rejected.")
            return self.response_post_save_change(request, obj)

        if "_distribute" in request.POST:
            from django.utils import timezone
            # 1. Update Platform Statuses
            obj.platform_statuses.update(status='distributed', distributed_at=timezone.now())
            
            # 2. Update Content (Songs/Albums)
            for content in obj.contents.all():
                if content.song:
                    content.song.is_released = True
                    content.song.release_status = 'released'
                    content.song.release_date = timezone.now().date()
                    content.song.save()
                if content.album:
                    content.album.is_released = True
                    content.album.release_date = timezone.now().date()
                    content.album.save()
                    # Also update album tracks if needed
                    content.album.songs.update(is_released=True, release_status='released', release_date=timezone.now().date())

            # 3. Update Request Status
            obj.status = 'released'
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
