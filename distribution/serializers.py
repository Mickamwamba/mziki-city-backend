from rest_framework import serializers
from .models import Platform, DistributionRequest, RevenueSplit, ReleaseRequest, ReleaseRequestContent, ReleaseRequestPlatform
from music.serializers import SongSerializer

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'

class RevenueSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSplit
        fields = ['id', 'song', 'album', 'recipient', 'role', 'percentage']

class ReleaseRequestPlatformSerializer(serializers.ModelSerializer):
    platform_details = PlatformSerializer(source='platform', read_only=True)
    
    class Meta:
        model = ReleaseRequestPlatform
        fields = ['id', 'platform', 'platform_details', 'status', 'external_id', 'distributed_at']

from music.serializers import SongSerializer, AlbumSerializer

class ReleaseRequestContentSerializer(serializers.ModelSerializer):
    song_details = SongSerializer(source='song', read_only=True)
    album_details = AlbumSerializer(source='album', read_only=True)
    
    class Meta:
        model = ReleaseRequestContent
        fields = ['id', 'song', 'song_details', 'album', 'album_details']

class ReleaseRequestSerializer(serializers.ModelSerializer):
    contents = ReleaseRequestContentSerializer(many=True, read_only=True)
    platform_statuses = ReleaseRequestPlatformSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReleaseRequest
        fields = ['id', 'artist', 'status', 'title', 'created_at', 'updated_at', 'contents', 'platform_statuses']
        read_only_fields = ['artist', 'created_at', 'updated_at', 'status']

class DistributionRequestSerializer(serializers.ModelSerializer):
    platform_details = PlatformSerializer(source='platform', read_only=True)
    song_details = SongSerializer(source='song', read_only=True)
    
    class Meta:
        model = DistributionRequest
        fields = ['id', 'song', 'song_details', 'platform', 'platform_details', 'status', 'distributed_at', 'external_id', 'created_at']
