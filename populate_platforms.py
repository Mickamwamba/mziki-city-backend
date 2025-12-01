import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from distribution.models import Platform

platforms = [
    "Spotify",
    "Apple Music",
    "YouTube Music",
    "Deezer",
    "Amazon Music",
    "Tidal",
    "Pandora",
    "SoundCloud",
    "Audiomack",
    "iHeartRadio"
]

print("Populating platforms...")
for name in platforms:
    platform, created = Platform.objects.get_or_create(name=name)
    if created:
        print(f"Created: {name}")
    else:
        print(f"Already exists: {name}")

print("Done!")
