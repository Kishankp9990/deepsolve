from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserPost, UserProfile, Follow, LikePost, CommentPost


User = get_user_model()

# serializer for user registration model
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),  # Provide a default value if email is missing
            password=validated_data['password']
        )
        return user

#serializer for login tracking model
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

#serializer for userpost model
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ['id', 'caption', 'post_url', 'background_music_url', 'category', 'datetime_posted', 'publisher', 'is_public']
        read_only_fields = ['datetime_posted', 'publisher']
        
#serializer for createuserprofile model
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Fetch username from the related user model
    class Meta:
        model = UserProfile
        fields = ['name', 'username', 'profile_pic', 'bio', 'dob']
        extra_kwargs = {
            'username': {'read_only': True},  # Username should not be editable
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
#serializer to follow other user
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']
        
# Like Serializer
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentPost
        fields = ['id', 'user', 'post', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        

