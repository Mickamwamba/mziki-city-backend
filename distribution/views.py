from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DistributionRequest, Platform, RevenueSplit, ReleaseRequest, ReleaseRequestContent, ReleaseRequestPlatform
from .serializers import DistributionRequestSerializer, PlatformSerializer, RevenueSplitSerializer, ReleaseRequestSerializer
from music.models import Song
from music.serializers import SongSerializer
from django.db.models import Max

class ReleaseRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ReleaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReleaseRequest.objects.filter(artist=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_release(self, request):
        # Expects: { "song_id": 1, "platform_ids": [1, 2], "splits": [...] }
        # Or for album: { "album_id": 1, ... }
        # For Label: { "artist_id": 5, ... }
        
        song_id = request.data.get('song_id')
        album_id = request.data.get('album_id')
        artist_id = request.data.get('artist_id')
        platform_ids = request.data.get('platform_ids', [])
        splits_data = request.data.get('splits', [])
        
        if not song_id and not album_id:
            return Response({"error": "Song ID or Album ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Determine the artist for this release
        release_artist = request.user
        if request.user.is_label:
            if not artist_id:
                return Response({"error": "Artist ID is required for label releases"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                release_artist = User.objects.get(id=artist_id, label=request.user)
            except User.DoesNotExist:
                return Response({"error": "Invalid artist or artist not managed by you"}, status=status.HTTP_403_FORBIDDEN)
        
        target_obj = None
        title = ""
        
        if song_id:
            try:
                target_obj = Song.objects.get(id=song_id, artist=release_artist)
                title = target_obj.title
            except Song.DoesNotExist:
                return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
        elif album_id:
            from music.models import Album
            try:
                target_obj = Album.objects.get(id=album_id, artist=release_artist)
                title = target_obj.title
            except Album.DoesNotExist:
                return Response({"error": "Album not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Create ReleaseRequest
        release_request = ReleaseRequest.objects.create(
            artist=release_artist,
            status='pending',
            title=title
        )

        # 2. Create Content
        if song_id:
            ReleaseRequestContent.objects.create(
                request=release_request,
                song=target_obj
            )
            # Update song status
            target_obj.release_status = 'pending'
            target_obj.save()
        elif album_id:
            # Add Album Content
            ReleaseRequestContent.objects.create(
                request=release_request,
                album=target_obj
            )
            # Add all songs in album as content too? Or just the album?
            # Let's add the album itself as the main content item.
            # We can also add individual songs if we want granular tracking, but for now album level is fine.
            
            # Update album status
            target_obj.is_released = False # It's pending
            # We don't have a release_status field on Album yet? Let's check. 
            # If not, we rely on is_released=False until approved.
            # But we should probably update the songs in the album to pending too.
            for song in target_obj.songs.all():
                song.release_status = 'pending'
                song.save()

        # 3. Create Platforms
        for pid in platform_ids:
            try:
                platform = Platform.objects.get(id=pid)
                ReleaseRequestPlatform.objects.create(
                    request=release_request,
                    platform=platform
                )
            except Platform.DoesNotExist:
                continue

        # 4. Handle Splits (Optional, if sent here)
        if splits_data:
            # If it's a song, we clear song splits. If album, album splits?
            # For now, simplistic handling:
            if song_id:
                RevenueSplit.objects.filter(song=target_obj).delete()
                for split in splits_data:
                    split['song'] = target_obj.id
                    serializer = RevenueSplitSerializer(data=split)
                    if serializer.is_valid():
                        serializer.save()
            elif album_id:
                RevenueSplit.objects.filter(album=target_obj).delete()
                for split in splits_data:
                    split['album'] = target_obj.id
                    serializer = RevenueSplitSerializer(data=split)
                    if serializer.is_valid():
                        serializer.save()

        return Response(ReleaseRequestSerializer(release_request).data, status=status.HTTP_201_CREATED)

class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.AllowAny]

class DistributionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DistributionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = DistributionRequest.objects.filter(song__artist=self.request.user).order_by('-created_at')
        song_id = self.request.query_params.get('song')
        if song_id:
            queryset = queryset.filter(song_id=song_id)
        return queryset

    def perform_create(self, serializer):
        # Ensure the song belongs to the user
        song = serializer.validated_data['song']
        if song.artist != self.request.user:
            raise permissions.PermissionDenied("You do not own this song.")
        serializer.save()

    @action(detail=False, methods=['post'])
    def distribute_song(self, request):
        song_id = request.data.get('song_id')
        platform_ids = request.data.get('platform_ids', [])

        try:
            song = Song.objects.get(id=song_id, artist=request.user)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)

        created_requests = []
        for pid in platform_ids:
            try:
                platform = Platform.objects.get(id=pid)
                dist_req, created = DistributionRequest.objects.get_or_create(
                    song=song,
                    platform=platform
                )
                # Always set to pending if re-submitting (or created)
                if dist_req.status != 'pending':
                    dist_req.status = 'pending'
                    dist_req.save()
                
                if created:
                    created_requests.append(dist_req)
            except Platform.DoesNotExist:
                continue
        
        # Update song status to pending
        if created_requests:
            song.release_status = 'pending'
            song.save()
        
        return Response(DistributionRequestSerializer(created_requests, many=True).data)

    @action(detail=False, methods=['get'])
    def recent_releases(self, request):
        # Get songs that have at least one distribution request, ordered by the most recent request
        songs = Song.objects.filter(
            distributions__isnull=False, 
            artist=request.user
        ).distinct().annotate(
            latest_request=Max('distributions__created_at')
        ).order_by('-latest_request')
        
        return Response(SongSerializer(songs, many=True).data)

class RevenueSplitViewSet(viewsets.ModelViewSet):
    queryset = RevenueSplit.objects.all()
    serializer_class = RevenueSplitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RevenueSplit.objects.all()
        song_id = self.request.query_params.get('song')
        album_id = self.request.query_params.get('album')
        
        if song_id:
            queryset = queryset.filter(song_id=song_id)
        if album_id:
            queryset = queryset.filter(album_id=album_id)
            
        return queryset

    @action(detail=False, methods=['post'])
    def set_splits(self, request):
        # Expects { "splits": [ { "recipient": "...", "role": "...", "percentage": 50, "song": 1 (optional), "album": 1 (optional) } ] }
        splits_data = request.data.get('splits', [])
        created_splits = []
        
        # Basic validation: ensure total percentage is 100 per entity? 
        # For now, we trust the frontend validation or just save what is sent.
        
        # Clear existing splits for the target entity to avoid duplicates/conflicts?
        # If we receive a list for a specific song/album, we should probably replace existing ones.
        
        # Group by entity to clear old ones
        songs_to_clear = set()
        albums_to_clear = set()
        
        for split in splits_data:
            if split.get('song'):
                songs_to_clear.add(split['song'])
            if split.get('album'):
                albums_to_clear.add(split['album'])
                
        RevenueSplit.objects.filter(song__in=songs_to_clear).delete()
        RevenueSplit.objects.filter(album__in=albums_to_clear).delete()

        for split_data in splits_data:
            serializer = self.get_serializer(data=split_data)
            if serializer.is_valid():
                serializer.save()
                created_splits.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(created_splits, status=status.HTTP_201_CREATED)
