from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'artist_name', 'bio', 'is_artist', 'is_label', 'label_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            artist_name=validated_data.get('artist_name', ''),
            label_name=validated_data.get('label_name', ''),
            bio=validated_data.get('bio', ''),
            is_artist=validated_data.get('is_artist', True),
            is_label=validated_data.get('is_label', False)
        )
        return user

class ManagedArtistSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'artist_name', 'bio', 'phone_number')
        extra_kwargs = {
            'email': {'required': True},
            'artist_name': {'required': True},
            'username': {'read_only': True}
        }

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Username will be email if not provided, or we can auto-generate
        username = validated_data.get('email')
        
        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            artist_name=validated_data.get('artist_name'),
            phone_number=validated_data.get('phone_number', ''),
            bio=validated_data.get('bio', ''),
            is_artist=True,
            is_label=False,
            label=self.context['request'].user # Link to the creating Label
        )
        return user
