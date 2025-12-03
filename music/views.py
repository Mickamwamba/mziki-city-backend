from rest_framework import viewsets, permissions
from .models import Song, Album
from .serializers import SongSerializer, AlbumSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Album.objects.filter(artist=user)
        
        if user.is_label:
            queryset = Album.objects.filter(artist__label=user) | Album.objects.filter(artist=user)
            
            artist_id = self.request.query_params.get('artist_id')
            if artist_id:
                queryset = queryset.filter(artist_id=artist_id)
                
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        artist = user
        if user.is_label:
            artist_id = self.request.data.get('artist_id')
            if artist_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    artist = User.objects.get(id=artist_id, label=user)
                except User.DoesNotExist:
                    pass # Fallback to user or raise error? For now fallback.
        serializer.save(artist=artist)

class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Song.objects.none()
        
        if user.is_label:
            queryset = Song.objects.filter(artist__label=user) | Song.objects.filter(artist=user)
            
            artist_id = self.request.query_params.get('artist_id')
            if artist_id:
                queryset = queryset.filter(artist_id=artist_id)
        else:
            queryset = Song.objects.filter(artist=user)

        status = self.request.query_params.get('release_status')
        if status:
            queryset = queryset.filter(release_status=status)
        
        # Support filtering by multiple statuses (comma separated)
        statuses = self.request.query_params.get('statuses')
        if statuses:
            status_list = statuses.split(',')
            queryset = queryset.filter(release_status__in=status_list)
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        artist = user
        if user.is_label:
            artist_id = self.request.data.get('artist_id')
            if artist_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    artist = User.objects.get(id=artist_id, label=user)
                except User.DoesNotExist:
                    pass
        serializer.save(artist=artist)
