from django.db import models
from music.models import Song

class Platform(models.Model):
    name = models.CharField(max_length=100) # e.g., Spotify, Apple Music
    api_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='platform_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class DistributionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('distributed', 'Distributed'),
        ('failed', 'Failed'),
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='distributions')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    distributed_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True) # ID on the platform

    def __str__(self):
        return f"{self.song.title} -> {self.platform.name} ({self.status})"

class RevenueSplit(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='revenue_splits', null=True, blank=True)
    # We can add Album support later if needed, or just apply to all songs in album
    # For now, let's support linking to Album directly for album-level splits
    from music.models import Album
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='revenue_splits', null=True, blank=True)
    
    recipient = models.CharField(max_length=255) # Name or Email
    role = models.CharField(max_length=100) # Artist, Label, Producer, Songwriter
    percentage = models.DecimalField(max_digits=5, decimal_places=2) # e.g. 50.00

    def __str__(self):
        return f"{self.recipient} ({self.percentage}%) - {self.song or self.album}"
