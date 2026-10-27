from django.db import models
from django.conf import settings

# User profile model for storing additional user information
class UserProfile(models.Model):
    """
    User profile model.
    
    Extends the default User model with additional profile information and customization options.
    Provides fields for personal details, profile image, and biographical information.
    Each profile is associated with exactly one user account.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Associated user account (one-to-one)
    nickname = models.CharField(max_length=50, blank=True)  # User's public display name
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # User's profile picture
    bio = models.TextField(blank=True)  # User's biographical information/description
    updated_at = models.DateTimeField(auto_now=True)  # When the profile was last updated (automatic)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Achievement(models.Model):
    """
    User achievement model.
    
    Stores achievement types that users can earn through various interactions.
    Achievements are granted based on user activity milestones.
    """
    ACHIEVEMENT_TYPES = [
        # Basic achievements
        ('first_review', 'Glorious First Trip'),
        ('first_post', 'New Poster'),
        ('first_like', 'You Liked It!'),
        
        # Content creation achievements
        ('reviews_5', 'Review Enthusiast'),
        ('reviews_10', 'Travel Critic'),
        ('reviews_25', 'Travel Expert'),
        ('posts_5', 'Content Creator'),
        ('posts_10', 'Community Contributor'),
        ('posts_25', 'Community Leader'),
        
        # Engagement achievements
        ('likes_10', 'Destination Fan'),
        ('likes_25', 'Destination Lover'),
        ('likes_50', 'Destination Aficionado'),
        
        # Profile achievements
        ('profile_complete', 'Identity Established'),
        ('bio_added', 'Storyteller'),
        
        # Activity duration achievements
        ('member_1_month', 'Rookie Traveler'),
        ('member_6_months', 'Seasoned Traveler'),
        ('member_1_year', 'Travel Veteran'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement_type')  # Each user can earn each achievement only once
    
    def __str__(self):
        achievement_name = dict(self.ACHIEVEMENT_TYPES).get(self.achievement_type, self.achievement_type)
        return f"{self.user.username} earned {achievement_name}"
    
    @classmethod
    def get_achievement_details(cls, achievement_type):
        """
        Get detailed information about an achievement type.
        
        Args:
            achievement_type: The type of achievement
            
        Returns:
            dict: Achievement details including name, description, and icon
        """
        details = {
            # Basic achievements
            'first_review': {
                'name': 'Glorious First Trip',
                'description': 'Write a review for your first destination',
                'icon': 'star',
                'category': 'basics'
            },
            'first_post': {
                'name': 'New Poster',
                'description': 'Write your first community post',
                'icon': 'edit',
                'category': 'basics'
            },
            'first_like': {
                'name': 'You Liked It!',
                'description': 'Like your first destination',
                'icon': 'heart',
                'category': 'basics'
            },
            
            # Content creation achievements
            'reviews_5': {
                'name': 'Review Enthusiast',
                'description': 'Write 5 destination reviews',
                'icon': 'star-half',
                'category': 'content'
            },
            'reviews_10': {
                'name': 'Travel Critic',
                'description': 'Write 10 destination reviews',
                'icon': 'star-fill',
                'category': 'content'
            },
            'reviews_25': {
                'name': 'Travel Expert',
                'description': 'Write 25 destination reviews',
                'icon': 'stars',
                'category': 'content'
            },
            'posts_5': {
                'name': 'Content Creator',
                'description': 'Write 5 community posts',
                'icon': 'pencil',
                'category': 'content'
            },
            'posts_10': {
                'name': 'Community Contributor',
                'description': 'Write 10 community posts',
                'icon': 'pencil-square',
                'category': 'content'
            },
            'posts_25': {
                'name': 'Community Leader',
                'description': 'Write 25 community posts',
                'icon': 'award',
                'category': 'content'
            },
            
            # Engagement achievements
            'likes_10': {
                'name': 'Destination Fan',
                'description': 'Like 10 destinations',
                'icon': 'heart-half',
                'category': 'engagement'
            },
            'likes_25': {
                'name': 'Destination Lover',
                'description': 'Like 25 destinations',
                'icon': 'heart-fill',
                'category': 'engagement'
            },
            'likes_50': {
                'name': 'Destination Aficionado',
                'description': 'Like 50 destinations',
                'icon': 'hearts',
                'category': 'engagement'
            },
            
            # Profile achievements
            'profile_complete': {
                'name': 'Identity Established',
                'description': 'Complete your profile information (gender, age range)',
                'icon': 'person-badge',
                'category': 'profile'
            },
            'bio_added': {
                'name': 'Storyteller',
                'description': 'Write your bio',
                'icon': 'chat-quote',
                'category': 'profile'
            },
            
            # Activity duration achievements
            'member_1_month': {
                'name': 'Rookie Traveler',
                'description': '1 month since joining',
                'icon': 'calendar',
                'category': 'time'
            },
            'member_6_months': {
                'name': 'Seasoned Traveler',
                'description': '6 months since joining',
                'icon': 'calendar2-check',
                'category': 'time'
            },
            'member_1_year': {
                'name': 'Travel Veteran',
                'description': '1 year since joining',
                'icon': 'calendar3',
                'category': 'time'
            },
        }
        return details.get(achievement_type, {})
