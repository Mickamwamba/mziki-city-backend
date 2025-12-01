from django.contrib import admin
from .models import Song, Album

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'is_released', 'created_at')
    list_filter = ('is_released', 'release_date')
    search_fields = ('title', 'artist__artist_name', 'artist__username')
    date_hierarchy = 'release_date'

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'genre', 'is_released', 'created_at')
    list_filter = ('is_released', 'genre', 'created_at')
    search_fields = ('title', 'artist__artist_name', 'artist__username', 'album__title')
    actions = ['mark_as_released', 'mark_as_unreleased']

    def mark_as_released(self, request, queryset):
        queryset.update(is_released=True)
    mark_as_released.short_description = "Mark selected songs as released"

    def mark_as_unreleased(self, request, queryset):
        queryset.update(is_released=False)
    mark_as_unreleased.short_description = "Mark selected songs as unreleased"
