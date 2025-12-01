from django.contrib import admin
from .models import Platform, DistributionRequest, RevenueSplit

@admin.register(RevenueSplit)
class RevenueSplitAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'role', 'percentage', 'get_content_object')
    list_filter = ('role',)
    search_fields = ('recipient', 'song__title', 'album__title')

    def get_content_object(self, obj):
        if obj.song:
            return f"Song: {obj.song.title}"
        elif obj.album:
            return f"Album: {obj.album.title}"
        return "-"
    get_content_object.short_description = "Content"

admin.site.register(Platform)

# admin.site.register(DistributionRequest) # Legacy model, hiding from admin to avoid confusion

from .models import ReleaseRequest, ReleaseRequestContent, ReleaseRequestPlatform

class ReleaseRequestContentInline(admin.TabularInline):
    model = ReleaseRequestContent
    extra = 0

class ReleaseRequestPlatformInline(admin.TabularInline):
    model = ReleaseRequestPlatform
    extra = 0

@admin.register(ReleaseRequest)
class ReleaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'artist__username', 'artist__email')
    inlines = [ReleaseRequestContentInline, ReleaseRequestPlatformInline]
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
