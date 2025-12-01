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
admin.site.register(DistributionRequest)
