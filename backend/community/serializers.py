from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class PostSerializer(serializers.ModelSerializer):
    """
    Post serializer.
    
    Serializes post data including author information.
    Returns both author username and ID for frontend reference.
    """
    author_id = serializers.ReadOnlyField(source='author.id')  # Return author_id 
    author = serializers.ReadOnlyField(source='author.username')  # Return username
    author_profile_image = serializers.SerializerMethodField()  # Add profile image field
    title = serializers.CharField(max_length=255, error_messages={
        'max_length': 'Title cannot exceed 255 characters.'
    })
    content = serializers.CharField(max_length=3000, error_messages={
        'max_length': 'Post content cannot exceed 3000 characters.'
    })

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_id', 'author_profile_image', 'created_at']

    def get_author_profile_image(self, obj):
        """
        Get the user's profile image URL.
        """
        from mypage.models import UserProfile
        try:
            # Get user profile information
            profile = UserProfile.objects.get(user=obj.author)
            return profile.profile_image.url if profile.profile_image else None
        except UserProfile.DoesNotExist:
            return None

class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer.
    
    Serializes comment data including author information.
    Author and post fields are read-only to prevent modification.
    """
    author_id = serializers.ReadOnlyField(source='author.id')  # Author ID field
    author = serializers.ReadOnlyField(source='author.username')  # Author field is read-only
    author_profile_image = serializers.SerializerMethodField()  # profile image field
    content = serializers.CharField(max_length=500, error_messages={
        'max_length': '댓글 내용은 500자를 초과할 수 없습니다.'
    })

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_id', 'author_profile_image', 'post', 'created_at']  # Include post field
        read_only_fields = ['post', 'author']  # Set post and author as read-only
        
    def get_author_profile_image(self, obj):
        """
        Get the user's profile image URL.
        """
        from mypage.models import UserProfile
        try:
            # Get user profile information
            profile = UserProfile.objects.get(user=obj.author)
            return profile.profile_image.url if profile.profile_image else None
        except UserProfile.DoesNotExist:
            return None