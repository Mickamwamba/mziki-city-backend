import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from distribution.models import DistributionRequest
from django.db.models import Count

def cleanup_duplicates():
    duplicates = DistributionRequest.objects.values('song', 'platform').annotate(count=Count('id')).filter(count__gt=1)
    
    print(f"Found {duplicates.count()} sets of duplicates.")
    
    for dup in duplicates:
        song_id = dup['song']
        platform_id = dup['platform']
        
        # Get all requests for this song/platform combo, ordered by created_at (newest first)
        requests = DistributionRequest.objects.filter(song_id=song_id, platform_id=platform_id).order_by('-created_at')
        
        # Keep the first one (newest), delete the rest
        to_delete = requests[1:]
        
        print(f"Cleaning up duplicates for Song {song_id}, Platform {platform_id}. Deleting {len(to_delete)} records.")
        
        for req in to_delete:
            req.delete()

if __name__ == '__main__':
    cleanup_duplicates()
