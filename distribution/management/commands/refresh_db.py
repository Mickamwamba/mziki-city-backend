from django.core.management.base import BaseCommand
from django.db import transaction
from music.models import Song, Album
from distribution.models import ReleaseRequest, ReleaseRequestContent, ReleaseRequestPlatform, DistributionRequest, RevenueSplit, Platform
from investments.models import UserSubscription
from analytics.models import StreamCount, Revenue, WithdrawalRequest

class Command(BaseCommand):
    help = 'Refreshes the database by deleting all application data except Platforms and System Config'

    def handle(self, *args, **options):
        self.stdout.write('Starting database refresh...')
        
        with transaction.atomic():
            # Analytics
            self.stdout.write('Deleting Analytics Data...')
            StreamCount.objects.all().delete()
            Revenue.objects.all().delete()
            WithdrawalRequest.objects.all().delete()

            # Investments
            self.stdout.write('Deleting Investments...')
            UserSubscription.objects.all().delete()
            # Preserving InvestmentProduct as it is likely system configuration
            
            # Distribution
            self.stdout.write('Deleting Release Requests...')
            ReleaseRequestPlatform.objects.all().delete()
            ReleaseRequestContent.objects.all().delete()
            ReleaseRequest.objects.all().delete()
            DistributionRequest.objects.all().delete() # Legacy
            RevenueSplit.objects.all().delete()
            
            # Music
            self.stdout.write('Deleting Music...')
            # Songs and Albums might be referenced by other things, but we are deleting most things.
            # Note: Deleting Song/Album will cascade delete related objects usually.
            Song.objects.all().delete()
            Album.objects.all().delete()
            
            # Verify Platforms exist
            platform_count = Platform.objects.count()
            self.stdout.write(f'Preserved {platform_count} Platforms.')
            
        self.stdout.write(self.style.SUCCESS('Database refreshed successfully!'))
