from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from .models import UserProfile, Achievement
from .serializers import UserProfileSerializer, AchievementSerializer, ProfileFactory, AchievementDecorator, StatsDecorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from community.models import Post
from destinations.models import Like, Review
import traceback
from django.contrib.auth import update_session_auth_hash

# ViewSet for handling user profile operations
class MyPageViewSet(viewsets.ViewSet):
    """
    ViewSet to handle user profile operations.
    Provides endpoints for retrieving and updating user profile information.
    Requires authentication for all operations.
    """
    permission_classes = [permissions.IsAuthenticated]  # User must be logged in to access these endpoints

    def retrieve(self, request):
        """
        Retrieves the profile of the currently authenticated user.
        Uses the decorator pattern to add achievements to the response.
        
        Returns:
            Response with serialized user profile data or error message.
        """
        print(f"[MyPageViewSet] Retrieve called for user: {request.user.username}")
        
        try:
            # Check if user profile exists
            print(f"[MyPageViewSet] Getting basic profile for user: {request.user.username}")
            profile = get_object_or_404(UserProfile, user=request.user)
            print(f"[MyPageViewSet] Basic profile found: {profile}")
            
            # Log progress for each step
            print("[MyPageViewSet] Starting decorator pattern")
            
            # Create decorated_profile from ProfileFactory
            try:
                print("[MyPageViewSet] Creating profile with ProfileFactory")
                decorated_profile = ProfileFactory.create_profile(
                    request.user, 
                    decorators=[AchievementDecorator, StatsDecorator]
                )
                print("[MyPageViewSet] Profile factory created profile successfully")
                
                # Get display data from decorated profile
                print("[MyPageViewSet] Getting display data from decorated profile")
                profile_data = decorated_profile.get_display_data()
                print("[MyPageViewSet] Display data retrieved successfully")
                
                return Response(profile_data, status=status.HTTP_200_OK)
            except Exception as decorator_error:
                # Error in decorator pattern - fallback to basic profile
                print(f"[MyPageViewSet] Error in decorator pattern: {str(decorator_error)}")
                print("[MyPageViewSet] Decorator error traceback:")
                traceback.print_exc()
                
                # Fallback to basic profile data
                print("[MyPageViewSet] Falling back to basic profile data")
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"[MyPageViewSet] Fatal error in retrieve: {str(e)}")
            print("[MyPageViewSet] Error traceback:")
            traceback.print_exc()
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request):
        """
        Updates the profile of the currently authenticated user.
        Supports partial updates for individual fields.
        
        Returns:
            Response with updated profile data or validation errors.
        """
        try:
            profile = get_object_or_404(UserProfile, user=request.user)  # Get profile for the current user
            
            # Handle age_group and gender update - update the user model directly
            if 'age_group' in request.data:
                user = request.user
                user.age_group = request.data.get('age_group')
                user.save()
                
            # Handle gender update
            if 'gender' in request.data:
                user = request.user
                user.gender = request.data.get('gender')
                user.save()
                
            # Update other profile fields through serializer
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=True  # Allow partial updates (only provided fields will be updated)
            )
            if serializer.is_valid():
                serializer.save()
                
                # Return fresh data with achievements using decorator pattern
                decorated_profile = ProfileFactory.create_profile(
                    request.user,
                    decorators=[AchievementDecorator, StatsDecorator]
                )
                profile_data = decorated_profile.get_display_data()
                
                return Response(profile_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AchievementViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user achievements.
    Provides endpoints for retrieving achievement information,
    including individual achievements and progress tracking.
    """
    permission_classes = [permissions.IsAuthenticated]  # User must be logged in to access

    def list(self, request):
        """
        List all achievements for the authenticated user.
        Includes achievement progress and overall statistics.
        
        Returns:
            Response with list of user achievements and statistics
        """
        try:
            achievements = Achievement.objects.filter(user=request.user).order_by('-earned_at')
            serializer = AchievementSerializer(achievements, many=True)
            
            # Get total possible achievements
            total_achievements = len(Achievement.ACHIEVEMENT_TYPES)
            achievement_percentage = int((len(achievements) / total_achievements) * 100) if total_achievements > 0 else 0
            
            # Get list of all possible achievement types
            all_achievement_types = []
            for achievement_type, _ in Achievement.ACHIEVEMENT_TYPES:
                details = Achievement.get_achievement_details(achievement_type)
                earned = achievements.filter(achievement_type=achievement_type).exists()
                
                all_achievement_types.append({
                    'achievement_type': achievement_type,
                    'name': details.get('name'),
                    'description': details.get('description'),
                    'icon': details.get('icon'),
                    'category': details.get('category', 'misc'),
                    'earned': earned,
                    'earned_at': achievements.filter(achievement_type=achievement_type).first().earned_at if earned else None
                })
            
            return Response({
                'achievements': serializer.data,
                'achievement_count': len(achievements),
                'achievement_percentage': achievement_percentage,
                'total_achievements': total_achievements,
                'all_achievement_types': all_achievement_types
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Retrieve details for a specific achievement.
        
        Args:
            pk: Achievement ID
            
        Returns:
            Response with achievement details
        """
        try:
            achievement = get_object_or_404(Achievement, id=pk, user=request.user)
            serializer = AchievementSerializer(achievement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        List all available achievement types, earned and not earned.
        
        Returns:
            Response with list of all achievement types and whether user has earned them
        """
        try:
            # Get user's earned achievements
            user_achievements = Achievement.objects.filter(user=request.user)
            earned_types = [a.achievement_type for a in user_achievements]
            
            # Configure achievement info by category
            categories = {
                'basics': {'name': 'basics', 'achievements': []},
                'content': {'name': 'content', 'achievements': []},
                'engagement': {'name': 'engagement', 'achievements': []},
                'profile': {'name': 'profile', 'achievements': []},
                'time': {'name': 'time', 'achievements': []},
                'misc': {'name': 'misc', 'achievements': []}
            }
            
            # Compile all achievement types with earned status
            for achievement_type, _ in Achievement.ACHIEVEMENT_TYPES:
                details = Achievement.get_achievement_details(achievement_type)
                achievement = user_achievements.filter(achievement_type=achievement_type).first()
                category = details.get('category', 'misc')
                
                achievement_info = {
                    'achievement_type': achievement_type,
                    'name': details.get('name'),
                    'description': details.get('description'),
                    'icon': details.get('icon'),
                    'earned': achievement_type in earned_types,
                    'earned_at': achievement.earned_at if achievement else None
                }
                
                # Add achievement to corresponding category
                if category in categories:
                    categories[category]['achievements'].append(achievement_info)
                else:
                    categories['misc']['achievements'].append(achievement_info)
                
            return Response({
                'categories': categories,
                'total_count': len(Achievement.ACHIEVEMENT_TYPES),
                'earned_count': len(earned_types),
                'percentage': int((len(earned_types) / len(Achievement.ACHIEVEMENT_TYPES)) * 100) if Achievement.ACHIEVEMENT_TYPES else 0
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def check_new(self, request):
        """
        Check for new achievements the user has earned but not yet been awarded.
        This endpoint will automatically create the achievements if criteria are met.
        
        Returns:
            Response with newly created achievements, if any
        """
        try:
            # Create basic profile and apply AchievementDecorator only
            basic_profile = ProfileFactory.create_profile(request.user, decorators=[])
            achievement_decorator = AchievementDecorator(basic_profile)
            new_achievements = achievement_decorator._check_and_create_achievements(request.user)
            
            return Response({
                'new_achievements': new_achievements,
                'count': len(new_achievements)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get user achievements grouped by categories.
        
        Returns:
            Response with achievements organized by categories
        """
        try:
            # All achievements for the user
            achievements = Achievement.objects.filter(user=request.user)
            
            # Categorize achievements by category
            categories = {}
            
            for achievement in achievements:
                details = Achievement.get_achievement_details(achievement.achievement_type)
                category_key = details.get('category', 'misc')
                
                if category_key not in categories:
                    # Map category names
                    category_names = {
                        'basics': 'basics',
                        'content': 'content',
                        'engagement': 'engagement',
                        'profile': 'profile',
                        'time': 'time',
                        'misc': 'misc'
                    }
                    
                    categories[category_key] = {
                        'name': category_names.get(category_key, 'misc'),
                        'achievements': []
                    }
                
                # Add achievement to category
                achievement_data = AchievementSerializer(achievement).data
                categories[category_key]['achievements'].append(achievement_data)
            
            return Response({
                'categories': categories,
                'total_count': achievements.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_achievements(request):
    """
    Get the authenticated user's achievements.
    
    Returns:
        Response with list of user achievements
    """
    try:
        # Use decorator pattern to create profile with achievements only
        profile = ProfileFactory.create_profile(request.user, decorators=[AchievementDecorator])
        profile_data = profile.get_display_data()
        
        # Extract achievement data only
        achievements = profile_data.get('achievements', [])
        achievement_count = profile_data.get('achievement_count', 0)
        achievement_percentage = profile_data.get('achievement_percentage', 0)
        total_achievements = len(Achievement.ACHIEVEMENT_TYPES)
        
        return Response({
            'achievements': achievements,
            'achievement_count': achievement_count,
            'achievement_percentage': achievement_percentage,
            'total_achievements': total_achievements
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    API to change user password.
    Requires old password verification and new password confirmation.
    
    Parameters:
        request: HTTP request with authenticated user, old_password, new_password, and confirm_password
        
    Returns:
        Response with success/error message and appropriate status code
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    # Validate request data
    if not old_password:
        return Response({"error": "Please enter your current password."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not new_password:
        return Response({"error": "Please enter a new password."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not confirm_password:
        return Response({"error": "Please enter your new password again."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify current password
    if not user.check_password(old_password):
        return Response({"error": "Current password does not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify new password matches confirmation
    if new_password != confirm_password:
        return Response({"error": "New password and confirmation password do not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Password length validation
    if len(new_password) < 8:
        return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    try:
        user.set_password(new_password)
        user.save()
        
        # Update session authentication hash to maintain login state
        update_session_auth_hash(request, user)
        
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)