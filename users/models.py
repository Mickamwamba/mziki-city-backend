from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_artist = models.BooleanField(default=True)
    artist_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
