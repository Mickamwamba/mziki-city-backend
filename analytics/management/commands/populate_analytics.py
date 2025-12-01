from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from music.models import Song
from distribution.models import Platform
from analytics.models import StreamCount, Revenue
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates analytics data for artist Ebenation'

    def handle(self, *args, **kwargs):
        try:
            artist = User.objects.get(artist_name='Ebenation')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with artist_name "Ebenation" not found'))
            return

        songs = Song.objects.filter(artist=artist)
        if not songs.exists():
            self.stdout.write(self.style.WARNING('No songs found for Ebenation'))
            return

        platforms = Platform.objects.all()
        if not platforms.exists():
            self.stdout.write(self.style.WARNING('No platforms found. Please populate platforms first.'))
            return

        # Clear existing data for these songs to avoid duplicates/mess
        StreamCount.objects.filter(song__in=songs).delete()
        Revenue.objects.filter(song__in=songs).delete()
        self.stdout.write(self.style.WARNING('Cleared existing analytics for Ebenation'))

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        total_streams = 0
        total_revenue = 0

        current_date = start_date
        while current_date <= end_date:
            for song in songs:
                for platform in platforms:
                    # Random streams between 0 and 1000
                    # Make some songs more popular
                    popularity_factor = 1 if song.id % 2 == 0 else 0.5
                    daily_streams = int(random.randint(0, 1000) * popularity_factor)
                    
                    if daily_streams > 0:
                        StreamCount.objects.create(
                            song=song,
                            platform=platform,
                            count=daily_streams,
                            date=current_date
                        )
                        total_streams += daily_streams

                        # Revenue approx $0.004 per stream
                        daily_revenue = daily_streams * 0.004
                        Revenue.objects.create(
                            song=song,
                            platform=platform,
                            amount=daily_revenue,
                            date=current_date
                        )
                        total_revenue += daily_revenue

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated data for {songs.count()} songs.'))
        self.stdout.write(self.style.SUCCESS(f'Total Streams: {total_streams}'))
        self.stdout.write(self.style.SUCCESS(f'Total Revenue: ${total_revenue:.2f}'))
