from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from music.models import Song
from distribution.models import Platform, RevenueSplit
from analytics.models import StreamCount, Revenue
from investments.models import InvestmentProduct, UserSubscription
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Adds a sample song with investment split and populates analytics'

    def handle(self, *args, **kwargs):
        try:
            artist = User.objects.get(artist_name='Ebenation')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with artist_name "Ebenation" not found'))
            return

        # Ensure NHIF Bima product exists
        try:
            product = InvestmentProduct.objects.get(name='NHIF Bima')
        except InvestmentProduct.DoesNotExist:
            self.stdout.write(self.style.ERROR('Investment Product "NHIF Bima" not found'))
            return

        # Ensure Subscription exists
        sub, created = UserSubscription.objects.get_or_create(
            user=artist,
            product=product,
            defaults={'percentage': 10.00}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created subscription to NHIF Bima'))
        else:
            self.stdout.write(self.style.SUCCESS('Found existing subscription to NHIF Bima'))

        # Create Song
        dummy_audio = ContentFile(b"dummy audio content", name="wekeza_future.mp3")
        dummy_image = ContentFile(b"dummy image content", name="wekeza_future_cover.jpg")

        song, created = Song.objects.get_or_create(
            title='Wekeza Future',
            artist=artist,
            defaults={
                'genre': 'Afro-Pop',
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

        # Create Revenue Split for NHIF Bima
        # Clear existing splits for this song to be safe
        RevenueSplit.objects.filter(song=song).delete()
        
        # 10% to NHIF Bima
        RevenueSplit.objects.create(
            song=song,
            recipient=product.name,
            role='Investment',
            percentage=10.00
        )
        # 90% to Artist
        RevenueSplit.objects.create(
            song=song,
            recipient='Me (Primary Artist)',
            role='Artist',
            percentage=90.00
        )
        self.stdout.write(self.style.SUCCESS(f'Created revenue splits: 10% to {product.name}, 90% to Artist'))

        # Populate Analytics
        platforms = Platform.objects.all()
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        total_streams = 0
        total_revenue = 0
        total_invested = 0

        current_date = start_date
        while current_date <= end_date:
            for platform in platforms:
                daily_streams = random.randint(100, 800)
                
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
                total_invested += daily_revenue * 0.10 # 10% investment
            
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Populated analytics for {song.title}'))
        self.stdout.write(self.style.SUCCESS(f'Total Streams: {total_streams}'))
        self.stdout.write(self.style.SUCCESS(f'Total Revenue: ${total_revenue:.2f}'))
        self.stdout.write(self.style.SUCCESS(f'Estimated Investment from this song: ${total_invested:.2f}'))
