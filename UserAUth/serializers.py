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
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'bio', 'avatar', 'avatar_url', 'is_google_account', 
                  'follower_count', 'following_count', 'date_joined', 'profile_updated_at')
        read_only_fields = ('id', 'email', 'is_google_account', 'follower_count', 
                            'following_count', 'date_joined', 'profile_updated_at')
    
    def get_avatar(self, obj):
        # Return uploaded avatar URL if exists, otherwise Google avatar URL
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return obj.avatar_url

class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ('username', 'bio', 'avatar')
    
    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
    def update(self, instance, validated_data):
        # Handle avatar upload
        avatar = validated_data.pop('avatar', None)
        if avatar:
            # Delete old avatar if exists
            if instance.avatar:
                instance.avatar.delete(save=False)
            instance.avatar = avatar
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
