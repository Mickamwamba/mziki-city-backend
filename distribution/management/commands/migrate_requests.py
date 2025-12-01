from django.core.management.base import BaseCommand
from django.db import transaction
from distribution.models import DistributionRequest, ReleaseRequest, ReleaseRequestContent, ReleaseRequestPlatform

class Command(BaseCommand):
    help = 'Migrates existing DistributionRequest objects to the new ReleaseRequest structure'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration...')
        
        # Group distribution requests by song
        # We can't easily use .values('song').annotate() because we need the actual objects
        # So we'll iterate and group manually or use a more complex query
        
        # Get all unique song IDs from DistributionRequest
        song_ids = DistributionRequest.objects.values_list('song', flat=True).distinct()
        
        count = 0
        with transaction.atomic():
            for song_id in song_ids:
                # Get all requests for this song
                requests = DistributionRequest.objects.filter(song_id=song_id)
                if not requests.exists():
                    continue
                
                # Assume the first request has the representative artist and created_at
                first_req = requests.first()
                artist = first_req.song.artist
                created_at = first_req.created_at
                
                # Determine overall status
                # If any is released -> released
                # If any is approved -> approved
                # Else -> pending (or whatever the default was)
                statuses = set(requests.values_list('status', flat=True))
                if 'released' in statuses:
                    overall_status = 'released'
                elif 'approved' in statuses:
                    overall_status = 'approved'
                elif 'rejected' in statuses:
                    overall_status = 'rejected'
                else:
                    overall_status = 'submitted' # Mapping 'pending' to 'submitted' or keeping 'pending'
                
                # Create ReleaseRequest
                release_request = ReleaseRequest.objects.create(
                    artist=artist,
                    title=first_req.song.title,
                    status=overall_status
                )
                # Manually set created_at since auto_now_add overrides it on creation
                release_request.created_at = created_at
                release_request.save()
                
                # Create Content
                ReleaseRequestContent.objects.create(
                    request=release_request,
                    song=first_req.song
                )
                
                # Create Platform entries
                for req in requests:
                    ReleaseRequestPlatform.objects.create(
                        request=release_request,
                        platform=req.platform,
                        status=req.status,
                        external_id=req.external_id,
                        distributed_at=req.distributed_at
                    )
                
                count += 1
                self.stdout.write(f'Migrated song: {first_req.song.title}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {count} releases'))
