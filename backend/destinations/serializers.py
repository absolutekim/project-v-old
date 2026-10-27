from rest_framework import serializers
from destinations.models import Location, Like, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    """
    Location serializer.
    
    Serializes the basic location model including all fields.
    Used for displaying location information in lists and search results.
    """
    class Meta:
        model = Location
        fields = '__all__'  # 🔹 Include all fields (including likes_count)

class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for public information.
    
    Provides a limited view of user data for security purposes.
    Only includes essential fields that are safe to expose.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class LikeSerializer(serializers.ModelSerializer):
    """
    Like serializer.
    
    Handles the relationship between users and locations they have liked.
    Includes nested user and location data for detailed views.
    """
    user = UserSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        source='location'
    )
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'location', 'location_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        """
        Create a like with the current user.
        
        Parameters:
            validated_data: Validated data dictionary
            
        Returns:
            Newly created Like instance
        """
        # Set the current requesting user as like.user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    """
    Review serializer.
    
    Handles user reviews for locations, including ratings and content.
    Includes sentiment analysis and provides related location and user information.
    Prevents users from submitting multiple reviews for the same location.
    """
    location_id = serializers.IntegerField(write_only=True, required=True)
    location_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    keywords = serializers.JSONField(required=False)
    author_id = serializers.ReadOnlyField(source='user.id')
    author_profile_image = serializers.SerializerMethodField()
    content = serializers.CharField(max_length=1000, error_messages={
        'max_length': 'Review content cannot exceed 1000 characters.'
    })
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'author_id', 'location', 'location_id', 'location_name', 
                 'username', 'author_profile_image', 'rating', 'content', 'sentiment', 
                 'keywords', 'created_at', 'updated_at']
        read_only_fields = ['user', 'location', 'sentiment', 'created_at', 'updated_at']
    
    def get_location_name(self, obj):
        """
        Get the name of the location associated with this review.
        
        Parameters:
            obj: Review instance
            
        Returns:
            str: Location name or None if location doesn't exist
        """
        return obj.location.name if obj.location else None
    
    def get_username(self, obj):
        """
        Get the username of the review author.
        
        Parameters:
            obj: Review instance
            
        Returns:
            str: Author username or None if user doesn't exist
        """
        return obj.user.username if obj.user else None
    
    def get_author_profile_image(self, obj):
        """
        Get the profile image URL of the review author.
        
        Parameters:
            obj: Review instance
            
        Returns:
            str: URL to the author's profile image or None if not available
        """
        from mypage.models import UserProfile
        try:
            # Get user profile information
            profile = UserProfile.objects.get(user=obj.user)
            return profile.profile_image.url if profile.profile_image else None
        except UserProfile.DoesNotExist:
            return None
    
    def create(self, validated_data):
        """
        Create a new review.
        
        Handles attaching the current user to the review, validating the location,
        and preventing duplicate reviews for the same location by a user.
        
        Parameters:
            validated_data: Validated data dictionary
            
        Returns:
            Newly created Review instance
            
        Raises:
            ValidationError: If location doesn't exist or user already reviewed this location
        """
        print("ReviewSerializer.create called:", validated_data)
        
        # if location_id is not in validated_data, raise an error
        if 'location_id' not in validated_data:
            raise serializers.ValidationError({"location_id": ["This field is required."]})
            
        location_id = validated_data.pop('location_id')
        user = self.context['request'].user
        
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise serializers.ValidationError({"location_id": ["Location does not exist."]})
        
        # Check if review already exists
        existing_review = Review.objects.filter(user=user, location=location).first()
        if existing_review:
            raise serializers.ValidationError({"error": "You have already written a review for this location."})
        
        review = Review.objects.create(
            user=user,
            location=location,
            **validated_data
        )
        return review
    
    def update(self, instance, validated_data):
        """
        Update an existing review.
        
        Allows updating of review content, rating, and optionally the location.
        
        Parameters:
            instance: Existing Review instance to update
            validated_data: Validated data dictionary with new values
            
        Returns:
            Updated Review instance
            
        Raises:
            ValidationError: If specified location doesn't exist
        """
        print("ReviewSerializer.update called:", validated_data)
        if 'location_id' in validated_data:
            location_id = validated_data.pop('location_id')
            try:
                location = Location.objects.get(id=location_id)
                instance.location = location
            except Location.DoesNotExist:
                raise serializers.ValidationError({"location_id": "Location does not exist."})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class LocationDetailSerializer(LocationSerializer):
    """
    Detailed location serializer.
    
    Extends the base LocationSerializer to include comprehensive information about a location,
    including review statistics, user interaction status (likes/reviews), and recent reviews.
    Used for single location detail views where more information is required than in list views.
    """
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_review = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = '__all__'
    
    def get_reviews_count(self, obj):
        """
        Get the total number of reviews for this location.
        
        Parameters:
            obj: Location instance
            
        Returns:
            int: Total number of reviews
        """
        return obj.reviews.count()
    
    def get_average_rating(self, obj):
        """
        Calculate the average rating from all reviews.
        
        Parameters:
            obj: Location instance
            
        Returns:
            float: Average rating or None if no reviews
        """
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()
    
    def get_user_has_liked(self, obj):
        """
        Check if the current user has liked this location.
        
        Parameters:
            obj: Location instance
            
        Returns:
            bool: True if user has liked, False otherwise
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_user_review(self, obj):
        """
        Get the current user's review for this location.
        
        Parameters:
            obj: Location instance
            
        Returns:
            dict: Serialized review data or None if user hasn't reviewed
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                review = obj.reviews.get(user=request.user)
                return ReviewSerializer(review).data
            except Review.DoesNotExist:
                return None
        return None
    
    def get_recent_reviews(self, obj):
        """
        Get the 5 most recent reviews for this location.
        
        Parameters:
            obj: Location instance
            
        Returns:
            list: List of serialized review data
        """
        # Return only the 5 most recent reviews
        reviews = obj.reviews.all()[:5]
        return ReviewSerializer(reviews, many=True).data
