from django.db import models
from django.conf import settings
from django.utils import timezone

class Location(models.Model):
    """
    Travel destination location model.
    
    Stores comprehensive information about travel destinations including geographic details,
    categorization, contact information, and metadata for search and display purposes.
    Locations can be liked and reviewed by users.
    """
    id = models.AutoField(primary_key=True)  # Primary key for the location
    name = models.CharField(max_length=255)  # Location name
    description = models.TextField(blank=True, null=True)  # Descriptive text about the location
    category = models.CharField(max_length=255, blank=True, null=True)  # Primary category (Restaurant, Attraction, etc.)
    subcategories = models.JSONField(blank=True, null=True)  # Subcategories stored as JSON
    subtypes = models.JSONField(blank=True, null=True)  # Subtypes for more specific categorization
    type = models.CharField(max_length=255, blank=True, null=True)  # Type of location

    # Address details
    address = models.CharField(max_length=500, blank=True, null=True)  # Full address
    city = models.CharField(max_length=255, blank=True, null=True)  # City name
    state = models.CharField(max_length=255, blank=True, null=True)  # State/province
    country = models.CharField(max_length=255, blank=True, null=True)  # Country
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # Postal/ZIP code
    street1 = models.CharField(max_length=255, blank=True, null=True)  # Street address line 1
    street2 = models.CharField(max_length=255, blank=True, null=True)  # Street address line 2

    # Geographic coordinates
    latitude = models.FloatField(blank=True, null=True)  # Latitude coordinate
    longitude = models.FloatField(blank=True, null=True)  # Longitude coordinate

    # Localized information
    local_address = models.CharField(max_length=500, blank=True, null=True)  # Address in local language
    local_name = models.CharField(max_length=255, blank=True, null=True)  # Name in local language
    location_string = models.CharField(max_length=500, blank=True, null=True)  # Formatted location string

    # Contact and media
    image = models.URLField(blank=True, null=True)  # URL to location image
    website = models.URLField(blank=True, null=True)  # Website URL
    email = models.EmailField(blank=True, null=True)  # Contact email
    
    # Metrics
    likes_count = models.IntegerField(default=0)  # Counter for likes (updated by Like model)

    def __str__(self):
        return self.name

# Like model
class Like(models.Model):
    """
    User like model.
    
    Represents a user's like on a specific location.
    Maintains a count of likes on the Location model and prevents duplicate likes.
    Implements custom save and delete methods to maintain data integrity.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')  # User who liked
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='likes')  # Location that was liked
    created_at = models.DateTimeField(auto_now_add=True)  # When the like was created
    
    class Meta:
        unique_together = ('user', 'location')  # Prevent duplicate likes from the same user on the same location
        ordering = ['-created_at']  # Order by most recent first
    
    def __str__(self):
        return f"{self.user.username} likes {self.location.name}"
    
    def save(self, *args, **kwargs):
        """
        Custom save method to handle like creation and location counter updates.
        
        Prevents duplicate likes and increments the likes_count on the associated location.
        
        Parameters:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            The saved Like instance or existing instance if already exists
        """
        # Increase location's likes_count when a new like is added
        is_new = self.pk is None
        
        # Check if it already exists (prevent duplicates)
        if is_new and Like.objects.filter(user=self.user, location=self.location).exists():
            # If already exists, return existing object instead of creating a new one
            return Like.objects.get(user=self.user, location=self.location)
        
        super().save(*args, **kwargs)
        
        if is_new:
            # For transaction safety, fetch the latest value from the database and update
            location = Location.objects.get(pk=self.location.pk)
            location.likes_count += 1
            location.save(update_fields=['likes_count'])
    
    def delete(self, *args, **kwargs):
        """
        Custom delete method to handle like removal and location counter updates.
        
        Decrements the likes_count on the associated location when a like is deleted.
        
        Parameters:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Decrease location's likes_count when a like is deleted
        location_id = self.location.id
        super().delete(*args, **kwargs)
        
        # For transaction safety, fetch the latest value from the database and update
        try:
            location = Location.objects.get(pk=location_id)
            location.likes_count = max(0, location.likes_count - 1)  # Ensure it doesn't go below zero
            location.save(update_fields=['likes_count'])
        except Location.DoesNotExist:
            # Ignore if the location has been deleted
            pass

# Review model
class Review(models.Model):
    """
    User review model.
    
    Stores user reviews for locations including ratings, content, and sentiment analysis.
    Reviews are automatically analyzed for sentiment and keywords when saved.
    Provides valuable user feedback and contributes to location recommendations.
    """
    RATING_CHOICES = (
        (1, '1 - Very Dissatisfied'),
        (2, '2 - Dissatisfied'),
        (3, '3 - Neutral'),
        (4, '4 - Satisfied'),
        (5, '5 - Very Satisfied'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')  # Review author
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews')  # Reviewed location
    content = models.TextField()  # Review text content
    rating = models.IntegerField(choices=RATING_CHOICES)  # Numerical rating (1-5)
    created_at = models.DateTimeField(auto_now_add=True)  # When the review was created
    updated_at = models.DateTimeField(auto_now=True)  # When the review was last updated
    
    # NLP analysis fields
    sentiment = models.CharField(max_length=20, null=True, blank=True)  # Sentiment classification (POSITIVE, NEGATIVE, NEUTRAL)
    sentiment_score = models.FloatField(null=True, blank=True)  # Sentiment confidence score (0-1)
    keywords = models.JSONField(null=True, blank=True)  # Keywords extracted from review content
    
    class Meta:
        ordering = ['-created_at']  # Order by most recent first
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.location.name}"
    
    def save(self, *args, **kwargs):
        """
        Custom save method to perform sentiment analysis on review content.
        
        Automatically analyzes the review text for sentiment and extracts keywords
        when the review is created or updated.
        
        Parameters:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            The saved Review instance
        """
        # Skip analysis if keywords are already provided
        if hasattr(self, '_skip_analysis') and self._skip_analysis:
            return super().save(*args, **kwargs)
            
        # Perform sentiment analysis when saving the review
        if self.content and not kwargs.get('no_analysis', False):
            try:
                from .review_utils import analyze_review
                analysis_result = analyze_review(self.content)
                
                self.sentiment = analysis_result.get('sentiment', 'NEUTRAL')
                self.sentiment_score = analysis_result.get('sentiment_score', 0.5)
                
                # Safe keyword storage
                if kwargs.get('skip_keywords', False):
                    # Skip keyword analysis
                    self.keywords = self.keywords or {'positive_keywords': [], 'negative_keywords': []}
                else:
                    # Store keywords in a safe structure format
                    self.keywords = {
                        'positive_keywords': analysis_result.get('positive_keywords', []),
                        'negative_keywords': analysis_result.get('negative_keywords', [])
                    }
            except Exception as e:
                print(f"Review analysis error: {str(e)}")
                # Use default sentiment in case of error
                if self.rating >= 4:
                    self.sentiment = 'POSITIVE'
                elif self.rating <= 2:
                    self.sentiment = 'NEGATIVE'
                else:
                    self.sentiment = 'NEUTRAL'
                    
                self.sentiment_score = 0.5
                self.keywords = {'positive_keywords': [], 'negative_keywords': []}
        
        super().save(*args, **kwargs)
