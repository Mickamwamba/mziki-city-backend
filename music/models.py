from django.db import models
from django.conf import settings

class Album(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    release_date = models.DateField(null=True, blank=True)
    cover_art = models.ImageField(upload_to='covers/', blank=True, null=True)
    
    # Release Metadata
    is_released = models.BooleanField(default=False)
    RELEASE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('released', 'Released'),
        ('rejected', 'Rejected'),
    ]
    release_status = models.CharField(max_length=20, choices=RELEASE_STATUS_CHOICES, default='draft')
    upc = models.CharField(max_length=100, blank=True)
    label_name = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100, blank=True)
    audio_file = models.FileField(upload_to='songs/')
    cover_art = models.ImageField(upload_to='song_covers/', blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Release Info
    is_released = models.BooleanField(default=False)
    RELEASE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('released', 'Released'),
        ('rejected', 'Rejected'),
    ]
    release_status = models.CharField(max_length=20, choices=RELEASE_STATUS_CHOICES, default='draft')
    genre = models.CharField(max_length=100)
    subgenre = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, default='English')
    label_name = models.CharField(max_length=255, blank=True)
    catalog_number = models.CharField(max_length=100, blank=True)
    explicit_content = models.CharField(max_length=20, choices=[
        ('not_explicit', 'Not Explicit'),
        ('explicit', 'Explicit'),
        ('clean', 'Clean')
    ], default='not_explicit')

    # Credits
    primary_artist_name = models.CharField(max_length=255, help_text="Name to be displayed as primary artist")
    featured_artists = models.CharField(max_length=1000, blank=True, help_text="Comma-separated list of featured artists")
    producer = models.CharField(max_length=255, blank=True, help_text="Producer name(s)")
    song_writer = models.CharField(max_length=255, blank=True, help_text="Song writer name(s)")
    
    # Rights
    composition_owner = models.CharField(max_length=255)
    composition_year = models.IntegerField(null=True, blank=True)
    master_recording_owner = models.CharField(max_length=255)
    master_recording_year = models.IntegerField(null=True, blank=True)

    # Settings
    release_date = models.DateField(null=True, blank=True)
    excluded_countries = models.CharField(max_length=1000, blank=True, help_text="Comma-separated list of country codes to exclude")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
