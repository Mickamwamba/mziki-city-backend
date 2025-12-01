from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'artist_name', 'is_artist', 'is_staff', 'date_joined')
    list_filter = ('is_artist', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'artist_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Artist Info', {'fields': ('is_artist', 'artist_name', 'phone_number')}),
    )

admin.site.register(User, CustomUserAdmin)
