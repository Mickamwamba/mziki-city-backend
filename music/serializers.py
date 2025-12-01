from rest_framework import serializers
from .models import Song, Album

class AlbumSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ('artist', 'created_at')

class SongSerializer(serializers.ModelSerializer):
    album_details = AlbumSerializer(source='album', read_only=True)

    class Meta:
        model = Song
        fields = '__all__'
        read_only_fields = ('artist', 'created_at')
