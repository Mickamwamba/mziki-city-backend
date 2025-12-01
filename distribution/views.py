from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DistributionRequest, Platform, RevenueSplit
from .serializers import DistributionRequestSerializer, PlatformSerializer, RevenueSplitSerializer
from music.models import Song

class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.AllowAny]

class DistributionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DistributionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DistributionRequest.objects.filter(song__artist=self.request.user)

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
                if created:
                    # Set to pending for admin review
                    dist_req.status = 'pending'
                    dist_req.save()
                    created_requests.append(dist_req)
            except Platform.DoesNotExist:
                continue
        
        # Update song status to pending
        if created_requests:
            song.release_status = 'pending'
            song.save()
        
        return Response(DistributionRequestSerializer(created_requests, many=True).data)

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
