from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from music.models import Song
from distribution.models import Platform
from analytics.models import StreamCount, Revenue
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Adds a sample song "Mimi na Wewe" for Ebenation and populates analytics'

    def handle(self, *args, **kwargs):
        try:
            artist = User.objects.get(artist_name='Ebenation')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with artist_name "Ebenation" not found'))
            return

        # Create dummy content
        dummy_audio = ContentFile(b"dummy audio content", name="mimi_na_wewe.mp3")
        dummy_image = ContentFile(b"dummy image content", name="mimi_na_wewe_cover.jpg")

        song, created = Song.objects.get_or_create(
            title='Mimi na Wewe',
            artist=artist,
            defaults={
                'genre': 'Bongo Flava',
                'language': 'Swahili',
                'is_released': True,
                'release_date': timezone.now().date(),
                'primary_artist_name': 'Ebenation',
                'composition_owner': 'Ebenation',
                'master_recording_owner': 'Ebenation',
                'audio_file': dummy_audio,
                'cover_art': dummy_image
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created song: {song.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Song already exists: {song.title}'))

        # Populate Analytics for this song
        platforms = Platform.objects.all()
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        total_streams = 0
        total_revenue = 0

        current_date = start_date
        while current_date <= end_date:
            for platform in platforms:
                daily_streams = random.randint(50, 500) # Give it some good numbers
                
                StreamCount.objects.create(
                    song=song,
                    platform=platform,
                    count=daily_streams,
                    date=current_date
                )
                total_streams += daily_streams

                daily_revenue = daily_streams * 0.004
                Revenue.objects.create(
                    song=song,
                    platform=platform,
                    amount=daily_revenue,
                    date=current_date
                )
                total_revenue += daily_revenue
            
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Populated analytics for {song.title}'))
        self.stdout.write(self.style.SUCCESS(f'Total Streams: {total_streams}'))
        self.stdout.write(self.style.SUCCESS(f'Total Revenue: ${total_revenue:.2f}'))
