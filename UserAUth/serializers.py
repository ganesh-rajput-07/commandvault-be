from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'bio', 'avatar', 'banner', 'is_google_account', 
                  'follower_count', 'following_count', 'date_joined', 'profile_updated_at')
        read_only_fields = ('id', 'email', 'is_google_account', 'follower_count', 
                            'following_count', 'date_joined', 'profile_updated_at')
    
    def get_avatar(self, obj):
        """
        Return avatar URL with smart priority:
        1. If uploaded avatar exists AND is < 1MB: use uploaded avatar
        2. If uploaded avatar > 1MB OR doesn't exist: use Google avatar URL
        3. If neither exists: return None
        """
        # Check uploaded avatar first
        if obj.avatar:
            try:
                # Check file size (1MB = 1,000,000 bytes)
                file_size = obj.avatar.size
                if file_size < 1000000:  # Less than 1MB
                    # Use uploaded avatar
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.avatar.url)
                    return obj.avatar.url
                else:
                    # File too large, fall back to Google URL if available
                    if obj.avatar_url:
                        return obj.avatar_url
            except Exception as e:
                # If there's any error reading the file, fall back to Google URL
                if obj.avatar_url:
                    return obj.avatar_url
        
        # No uploaded avatar, use Google URL if available
        if obj.avatar_url:
            return obj.avatar_url
        
        # No avatar available
        return None
    
    def get_banner(self, obj):
        # Return uploaded banner URL if exists
        if obj.banner:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner.url)
            return obj.banner.url
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    banner = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ('username', 'bio', 'avatar', 'banner', 'avatar_url')
    
    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
    def validate_avatar(self, value):
        """Validate avatar file size (max 1MB)"""
        if value:
            # Check file size (1MB = 1,000,000 bytes)
            if value.size > 1000000:
                raise serializers.ValidationError(
                    "Avatar file size must be less than 1MB. "
                    "Please upload a smaller image or use your Google profile picture."
                )
        return value
    
    def validate_banner(self, value):
        """Validate banner file size (max 5MB)"""
        if value:
            # Check file size (5MB = 5,000,000 bytes)
            if value.size > 5000000:
                raise serializers.ValidationError(
                    "Banner file size must be less than 5MB. "
                    "Please upload a smaller image."
                )
        return value
    
    def update(self, instance, validated_data):
        # Handle avatar upload
        avatar = validated_data.pop('avatar', None)
        # Check if avatar_url is being updated (it might be in validated_data)
        avatar_url = validated_data.get('avatar_url')

        if avatar:
            # Delete old avatar if exists
            if instance.avatar:
                instance.avatar.delete(save=False)
            instance.avatar = avatar
            # We don't necessarily need to clear avatar_url, but instance.avatar takes priority anyway.
        elif avatar_url:
             # If setting a URL and NOT a file, allows switching to URL.
             # We should clear the existing file so the URL takes priority in get_avatar.
             if instance.avatar:
                 instance.avatar.delete(save=False)
                 instance.avatar = None

        # Handle banner upload
        banner = validated_data.pop('banner', None)
        if banner:
            # Delete old banner if exists
            if instance.banner:
                instance.banner.delete(save=False)
            instance.banner = banner
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
