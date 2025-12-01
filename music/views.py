from rest_framework import viewsets, permissions
from .models import Song, Album
from .serializers import SongSerializer, AlbumSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(artist=self.request.user)

    def perform_create(self, serializer):
        serializer.save(artist=self.request.user)

class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Song.objects.filter(artist=self.request.user)
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
        serializer.save(artist=self.request.user)
