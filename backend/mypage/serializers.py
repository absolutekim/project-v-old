from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Achievement
from abc import ABC, abstractmethod
from django.db.models import Count
from community.models import Post
from destinations.models import Like, Review
from django.utils import timezone
from datetime import timedelta
import traceback

User = get_user_model()

# Serializer for the User model with limited fields for security
class UserSerializer(serializers.ModelSerializer):
    """
    User data serializer.
    
    Serializes the User model with only essential fields for security.
    Provides a limited public view of user data, excluding sensitive information.
    All fields are read-only to prevent unauthorized modification through this serializer.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'age_group', 'gender')
        read_only_fields = ('id', 'username', 'email')  # These fields cannot be modified through this serializer

# Serializer for Achievement model
class AchievementSerializer(serializers.ModelSerializer):
    """
    Achievement serializer.
    
    Serializes achievement data including detailed information about each achievement.
    """
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = ('id', 'achievement_type', 'name', 'description', 'icon', 'category', 'earned_at')
    
    def get_name(self, obj):
        """Get achievement display name"""
        details = Achievement.get_achievement_details(obj.achievement_type)
        return details.get('name', obj.get_achievement_type_display())
    
    def get_description(self, obj):
        """Get achievement description"""
        details = Achievement.get_achievement_details(obj.achievement_type)
        return details.get('description', '')
    
    def get_icon(self, obj):
        """Get achievement icon name"""
        details = Achievement.get_achievement_details(obj.achievement_type)
        return details.get('icon', 'trophy')
        
    def get_category(self, obj):
        """Get achievement category"""
        details = Achievement.get_achievement_details(obj.achievement_type)
        return details.get('category', 'misc')

# Serializer for the UserProfile model including the related User data
class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer.
    
    Serializes the UserProfile model with nested User information.
    Used for retrieving and updating user profile information including 
    nickname, profile image, and biographical information.
    Includes the associated user data but prevents modification of user fields.
    """
    user = UserSerializer()  # Nested serializer for the related User model
    achievements = serializers.SerializerMethodField()
    achievement_count = serializers.SerializerMethodField()
    achievement_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'nickname', 'profile_image', 'bio', 'updated_at', 
                 'achievements', 'achievement_count', 'achievement_percentage')
        read_only_fields = ('id', 'user', 'updated_at')  # These fields cannot be modified through this serializer
    
    def get_achievements(self, obj):
        """Get user's earned achievements"""
        achievements = Achievement.objects.filter(user=obj.user)
        return AchievementSerializer(achievements, many=True).data
    
    def get_achievement_count(self, obj):
        """Get the count of user's earned achievements"""
        return Achievement.objects.filter(user=obj.user).count()
    
    def get_achievement_percentage(self, obj):
        """Calculate percentage of achievements earned by the user"""
        total_achievements = len(Achievement.ACHIEVEMENT_TYPES)
        earned_achievements = Achievement.objects.filter(user=obj.user).count()
        
        if total_achievements > 0:
            return int((earned_achievements / total_achievements) * 100)
        return 0

# --- Decorator Pattern Implementation ---

class UserProfileComponent(ABC):
    """
    Base component interface for user profile objects.
    Following the decorator pattern.
    """
    
    @abstractmethod
    def get_display_data(self):
        """
        Return display data for the user profile.
        
        Returns:
            dict: Display data for the profile
        """
        pass


class BasicUserProfile(UserProfileComponent):
    """
    Concrete component implementation for basic user profile.
    """
    
    def __init__(self, user):
        """
        Initialize with a user object.
        
        Args:
            user: User instance
        """
        self.user = user
        self.profile = self._get_profile()
    
    def _get_profile(self):
        """Get or create user profile"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        return profile
    
    def get_display_data(self):
        """
        Get basic profile display data.
        
        Returns:
            dict: Basic profile data
        """
        return {
            'id': self.profile.id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'gender': self.user.gender,
                'age_group': self.user.age_group,
            },
            'nickname': self.profile.nickname,
            'profile_image': self.profile.profile_image.url if self.profile.profile_image else None,
            'bio': self.profile.bio,
            'updated_at': self.profile.updated_at,
        }


class ProfileDecorator(UserProfileComponent):
    """
    Abstract decorator for user profile components.
    """
    
    def __init__(self, wrapped_component):
        """
        Initialize with a component to wrap.
        
        Args:
            wrapped_component: The component being decorated
        """
        self.wrapped = wrapped_component
        # Add user property to easily access it through the decorator chain
        if hasattr(wrapped_component, 'user'):
            self.user = wrapped_component.user
    
    def get_display_data(self):
        """
        Get data from wrapped component.
        
        Returns:
            dict: Data from wrapped component
        """
        return self.wrapped.get_display_data()


class AchievementDecorator(ProfileDecorator):
    """
    Decorator that adds achievements to user profile data.
    """
    
    def get_display_data(self):
        """
        Extend profile data with achievements.
        
        Returns:
            dict: Profile data with achievements
        """
        # Change the way to access user information - safer approach
        user_info = ""
        user = None
        if hasattr(self, 'user'):
            user = self.user
            user_info = user.username
        elif hasattr(self.wrapped, 'user'):
            user = self.wrapped.user
            user_info = user.username
        else:
            user_info = "unknown"
        
        print(f"[AchievementDecorator] Getting display data for user: {user_info}")
        try:
            data = super().get_display_data()
            
            # Get user achievements
            if not user:
                # Try to get user from data if not available directly
                if 'user' in data and isinstance(data['user'], dict) and 'id' in data['user']:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=data['user']['id'])
                    print(f"[AchievementDecorator] Found user from data: {user.username}")
            
            if not user:
                print("[AchievementDecorator] Error: User not found, cannot process achievements")
                data['achievements'] = []
                data['achievement_count'] = 0
                data['achievement_percentage'] = 0
                return data
            
            print("[AchievementDecorator] Checking for achievements")
            try:
                self._check_and_create_achievements(user)
                print("[AchievementDecorator] Achievement check completed")
            except Exception as achieve_error:
                print(f"[AchievementDecorator] Error checking achievements: {str(achieve_error)}")
                print("[AchievementDecorator] Achievement check error traceback:")
                traceback.print_exc()
                # Continue execution even if achievement check fails
            
            # Format achievements
            print("[AchievementDecorator] Formatting achievements")
            try:
                achievements_data = self._format_achievements(user)
                print(f"[AchievementDecorator] Found {len(achievements_data)} achievements")
                
                # Calculate percentage
                achievement_percentage = self._calculate_percentage(user)
                
                # Add data to profile
                data['achievements'] = achievements_data
                data['achievement_count'] = len(achievements_data)
                data['achievement_percentage'] = achievement_percentage
                
                print("[AchievementDecorator] Achievement data added to profile")
                return data
            except Exception as format_error:
                print(f"[AchievementDecorator] Error formatting achievements: {str(format_error)}")
                print("[AchievementDecorator] Format error traceback:")
                traceback.print_exc()
                # Return data without achievements
                return data
        except Exception as e:
            print(f"[AchievementDecorator] Fatal error in get_display_data: {str(e)}")
            print("[AchievementDecorator] Error traceback:")
            traceback.print_exc()
            # Try to return original data if possible
            try:
                return super().get_display_data()
            except:
                # Return empty dict as last resort
                return {}
    
    def _get_achievements(self, user):
        """Get user's current achievements"""
        return Achievement.objects.filter(user=user)
    
    def _check_and_create_achievements(self, user):
        """
        Check for and create new achievements the user has earned.
        
        Args:
            user: User object to check achievements for
            
        Returns:
            list: Newly created achievements
        """
        new_achievements = []
        
        # --- Basic Achievements ---
        # First review
        if not Achievement.objects.filter(user=user, achievement_type='first_review').exists():
            if Review.objects.filter(user=user).exists():
                achievement = Achievement.objects.create(user=user, achievement_type='first_review')
                new_achievements.append(self._format_achievement(achievement))
        
        # First post
        if not Achievement.objects.filter(user=user, achievement_type='first_post').exists():
            if Post.objects.filter(author=user).exists():
                achievement = Achievement.objects.create(user=user, achievement_type='first_post')
                new_achievements.append(self._format_achievement(achievement))
        
        # First like
        if not Achievement.objects.filter(user=user, achievement_type='first_like').exists():
            if Like.objects.filter(user=user).exists():
                achievement = Achievement.objects.create(user=user, achievement_type='first_like')
                new_achievements.append(self._format_achievement(achievement))
        
        # --- Content Creation Achievements ---
        # Achievements based on review count
        review_count = Review.objects.filter(user=user).count()
        
        if review_count >= 5 and not Achievement.objects.filter(user=user, achievement_type='reviews_5').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='reviews_5')
            new_achievements.append(self._format_achievement(achievement))
            
        if review_count >= 10 and not Achievement.objects.filter(user=user, achievement_type='reviews_10').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='reviews_10')
            new_achievements.append(self._format_achievement(achievement))
            
        if review_count >= 25 and not Achievement.objects.filter(user=user, achievement_type='reviews_25').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='reviews_25')
            new_achievements.append(self._format_achievement(achievement))
        
        # Achievements based on post count
        post_count = Post.objects.filter(author=user).count()
        
        if post_count >= 5 and not Achievement.objects.filter(user=user, achievement_type='posts_5').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='posts_5')
            new_achievements.append(self._format_achievement(achievement))
            
        if post_count >= 10 and not Achievement.objects.filter(user=user, achievement_type='posts_10').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='posts_10')
            new_achievements.append(self._format_achievement(achievement))
            
        if post_count >= 25 and not Achievement.objects.filter(user=user, achievement_type='posts_25').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='posts_25')
            new_achievements.append(self._format_achievement(achievement))
        
        # --- Participation Achievements ---
        # Achievements based on like count
        like_count = Like.objects.filter(user=user).count()
        
        if like_count >= 10 and not Achievement.objects.filter(user=user, achievement_type='likes_10').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='likes_10')
            new_achievements.append(self._format_achievement(achievement))
            
        if like_count >= 25 and not Achievement.objects.filter(user=user, achievement_type='likes_25').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='likes_25')
            new_achievements.append(self._format_achievement(achievement))
            
        if like_count >= 50 and not Achievement.objects.filter(user=user, achievement_type='likes_50').exists():
            achievement = Achievement.objects.create(user=user, achievement_type='likes_50')
            new_achievements.append(self._format_achievement(achievement))
        
        # --- Profile Achievements ---
        # Profile completion achievement
        if not Achievement.objects.filter(user=user, achievement_type='profile_complete').exists():
            if user.gender and user.age_group:
                achievement = Achievement.objects.create(user=user, achievement_type='profile_complete')
                new_achievements.append(self._format_achievement(achievement))
        
        # Bio added achievement
        if not Achievement.objects.filter(user=user, achievement_type='bio_added').exists():
            if hasattr(user, 'userprofile') and user.userprofile.bio and len(user.userprofile.bio.strip()) > 10:
                achievement = Achievement.objects.create(user=user, achievement_type='bio_added')
                new_achievements.append(self._format_achievement(achievement))
        
        # --- Activity Period Achievements ---
        # Achievements based on joining date
        join_date = user.date_joined
        now = timezone.now()
        
        # 1 month achievement
        if not Achievement.objects.filter(user=user, achievement_type='member_1_month').exists():
            if (now - join_date) >= timedelta(days=30):
                achievement = Achievement.objects.create(user=user, achievement_type='member_1_month')
                new_achievements.append(self._format_achievement(achievement))
        
        # 6 months achievement
        if not Achievement.objects.filter(user=user, achievement_type='member_6_months').exists():
            if (now - join_date) >= timedelta(days=180):
                achievement = Achievement.objects.create(user=user, achievement_type='member_6_months')
                new_achievements.append(self._format_achievement(achievement))
        
        # 1 year achievement
        if not Achievement.objects.filter(user=user, achievement_type='member_1_year').exists():
            if (now - join_date) >= timedelta(days=365):
                achievement = Achievement.objects.create(user=user, achievement_type='member_1_year')
                new_achievements.append(self._format_achievement(achievement))
                
        return new_achievements
    
    def _format_achievement(self, achievement):
        """Format a single achievement for display"""
        details = Achievement.get_achievement_details(achievement.achievement_type)
        return {
            'id': achievement.id,
            'achievement_type': achievement.achievement_type,
            'name': details.get('name', achievement.get_achievement_type_display()),
            'description': details.get('description', ''),
            'icon': details.get('icon', 'trophy'),
            'category': details.get('category', 'misc'),
            'earned_at': achievement.earned_at,
        }
    
    def _format_achievements(self, user):
        """Format achievements for display"""
        achievements = Achievement.objects.filter(user=user)
        return [self._format_achievement(achievement) for achievement in achievements]
    
    def _calculate_percentage(self, user):
        """Calculate percentage of achievements earned"""
        total_achievements = len(Achievement.ACHIEVEMENT_TYPES)
        earned_achievements = Achievement.objects.filter(user=user).count()
        
        if total_achievements > 0:
            return int((earned_achievements / total_achievements) * 100)
        return 0


class ProfileFactory:
    """
    Factory for creating decorated user profiles.
    Provides flexible creation of user profile objects with various decorators.
    """
    
    @staticmethod
    def create_profile(user, decorators=None):
        """
        Create a user profile with specified decorators.
        
        Args:
            user: User object
            decorators: List of decorator classes to apply
            
        Returns:
            UserProfileComponent: Decorated user profile
        """
        # Create basic profile
        profile = BasicUserProfile(user)
        
        # Apply decorators in order if specified
        if decorators:
            for decorator in decorators:
                profile = decorator(profile)
        
        return profile
    
    @staticmethod
    def create_full_profile(user):
        """
        Creates a complete profile with all decorators applied.
        
        Args:
            user: User object
            
        Returns:
            UserProfileComponent: Profile with all decorators applied
        """
        return ProfileFactory.create_profile(
            user, 
            decorators=[AchievementDecorator, StatsDecorator]
        )
    
    @staticmethod
    def create_basic_profile(user):
        """
        Creates a basic profile without decorators.
        
        Args:
            user: User object
            
        Returns:
            UserProfileComponent: Basic profile
        """
        return ProfileFactory.create_profile(user, decorators=[])

# User statistics decorator
class StatsDecorator(ProfileDecorator):
    """
    Decorator that adds user statistics to profile data.
    """
    
    def get_display_data(self):
        """
        Extend profile data with user statistics.
        
        Returns:
            dict: Profile data with statistics
        """
        # Change the way to access user information - safer approach
        user_info = ""
        if hasattr(self, 'user'):
            user_info = self.user.username
        elif hasattr(self.wrapped, 'user'):
            user_info = self.wrapped.user.username
        else:
            user_info = "unknown"
        
        print(f"[StatsDecorator] Getting display data for user: {user_info}")
        try:
            data = super().get_display_data()
            
            # Calculate statistics
            try:
                print("[StatsDecorator] Calculating user statistics")
                # Get user object for statistics calculation
                user = None
                if hasattr(self, 'user'):
                    user = self.user
                else:
                    # Find user object using alternative methods if needed
                    # (here we can use user_id from data)
                    if 'user' in data and isinstance(data['user'], dict) and 'id' in data['user']:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(id=data['user']['id'])
                
                if user:
                    stats = self._calculate_stats(user)
                    
                    # Add statistics to data
                    data['stats'] = stats
                    print("[StatsDecorator] Statistics added to profile data")
                else:
                    print("[StatsDecorator] Warning: User object not found, skipping statistics")
                    data['stats'] = {
                        'error': 'User not found',
                        'posts': 0,
                        'reviews': 0,
                        'likes': 0,
                        'days_active': 0,
                        'recent_activity': 0
                    }
                
                return data
            except Exception as stats_error:
                print(f"[StatsDecorator] Error calculating statistics: {str(stats_error)}")
                print("[StatsDecorator] Statistics error traceback:")
                traceback.print_exc()
                # Return data without statistics
                return data
        except Exception as e:
            print(f"[StatsDecorator] Fatal error in get_display_data: {str(e)}")
            print("[StatsDecorator] Error traceback:")
            traceback.print_exc()
            # Try to return original data if possible
            try:
                return super().get_display_data()
            except:
                # Return empty dict as last resort
                return {}
    
    def _calculate_stats(self, user):
        """
        Calculate user statistics.
        
        Args:
            user: User object
            
        Returns:
            dict: User statistics
        """
        # Post statistics
        post_count = Post.objects.filter(author=user).count()
        
        # Review statistics
        review_count = Review.objects.filter(user=user).count()
        
        # Like statistics
        like_count = Like.objects.filter(user=user).count()
        
        # Activity period statistics
        days_since_joined = (timezone.now().date() - user.date_joined.date()).days
        
        # Recent activity statistics (last 30 days)
        last_month = timezone.now() - timedelta(days=30)
        recent_posts = Post.objects.filter(author=user, created_at__gte=last_month).count()
        recent_reviews = Review.objects.filter(user=user, created_at__gte=last_month).count()
        recent_likes = Like.objects.filter(user=user, created_at__gte=last_month).count()
        recent_activity = recent_posts + recent_reviews + recent_likes
        
        return {
            'posts': post_count,
            'reviews': review_count,
            'likes': like_count,
            'days_active': days_since_joined,
            'recent_activity': recent_activity,
            'recent_posts': recent_posts,
            'recent_reviews': recent_reviews,
            'recent_likes': recent_likes
        }
