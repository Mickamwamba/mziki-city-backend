from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_artist = models.BooleanField(default=True)
    is_label = models.BooleanField(default=False)
    artist_name = models.CharField(max_length=255, blank=True, null=True)
    label_name = models.CharField(max_length=255, blank=True, null=True)
    label = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='artists')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
