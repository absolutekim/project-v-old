from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.serializers import RegisterSerializer, UserProfileDetailSerializer
from django.contrib.auth import authenticate, update_session_auth_hash
from django.db import connection
from accounts.models import CustomUser
from mypage.models import UserProfile
from django.shortcuts import get_object_or_404

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that extends the default TokenObtainPairView.
    Returns username along with the JWT tokens for better client-side user management.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Authenticate the logged-in user
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)  # Authentication process

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)  # Return 401 on authentication failure

        # Return username instead of user_id in the response
        response.data['username'] = user.username  

        return response

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow access without authentication
def register_user(request):
    """
    User registration endpoint.
    Creates a new user account using the provided data.
    
    Parameters:
        request: HTTP request with user registration data
        
    Returns:
        Response with success/error message and appropriate status code
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_subcategory_tags(request):
    """
    API to retrieve travel destination tags - extracting only subcategory0.
    Gets a list of unique subcategories from the destinations database.
    
    Parameters:
        request: HTTP request
        
    Returns:
        Response with list of subcategory tags
    """
    with connection.cursor() as cursor:
        # Query to extract only the exact subcategory0 list
        cursor.execute("""
            SELECT DISTINCT json_extract(subcategories, '$[0]') AS first_subcategory
            FROM destinations_location
            WHERE json_extract(subcategories, '$[0]') IS NOT NULL
            ORDER BY first_subcategory;
        """)
        subcategories = [row[0] for row in cursor.fetchall() if row[0]]
        
    return Response({"tags": subcategories}, status=status.HTTP_200_OK)

# This is spare codes that used to get user profile, but now it is replaced. 
# However, to do not corrupt system, it's being kept.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    API to retrieve profile information of the logged-in user.
    Returns user data including username, email, nickname, gender, and selected tags.
    
    Parameters:
        request: HTTP request with authenticated user
        
    Returns:
        Response with user profile data
    """
    user = request.user
    
    return Response({
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "gender": user.gender,
        "selected_tags": user.selected_tags
    }, status=status.HTTP_200_OK)

# This was spare codes that used to update user tags, but now it is not used anymore since it is considered as less-useful. 
# However, to do not corrupt system, it's being kept.
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_tags(request):
    """
    API to update user's tag information.
    Updates the user's selected tags with validation for tag count.
    
    Parameters:
        request: HTTP request with authenticated user and new tags
        
    Returns:
        Response with success/error message and updated tags
    """
    user = request.user
    selected_tags = request.data.get('selected_tags', [])
    
    # Validate tag count
    if len(selected_tags) < 3 or len(selected_tags) > 7:
        return Response({"error": "You must select between 3 and 7 tags."}, status=status.HTTP_400_BAD_REQUEST)
    
    user.selected_tags = selected_tags
    user.save()
    
    return Response({
        "message": "Tags have been successfully updated.",
        "selected_tags": user.selected_tags
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_account(request):
    """
    API to delete a user account.
    Deletes the user account after confirming password.
    
    Parameters:
        request: HTTP request with authenticated user and password confirmation
        
    Returns:
        Response with success/error message and appropriate status code
    """
    user = request.user
    user_id = user.id
    username = user.username
    
    # Password confirmation
    password = request.data.get('password')
    if not password:
        return Response({"error": "Please enter your password."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Password validation
    if not user.check_password(password):
        return Response({"error": "The password does not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Account deletion
    try:
        # 1. Delete UserProfile (ORM and Raw SQL both used)
        deleted_count = 0
        
        # 1.1 Try to delete using ORM
        from mypage.models import UserProfile
        try:
            profile = UserProfile.objects.filter(user=user).first()
            if profile:
                profile_id = profile.id
                profile.delete()
                deleted_count += 1
        except Exception:
            pass
        
        # 1.2 Try to delete using Raw SQL (in case ORM missed some records)
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM mypage_userprofile WHERE user_id = %s", [user_id])
                count = cursor.fetchone()[0]
                if count > 0:
                    cursor.execute("DELETE FROM mypage_userprofile WHERE user_id = %s", [user_id])
                    deleted_count += count
        except Exception:
            pass
        
        # 2. Delete likes data
        try:
            from destinations.models import Like
            likes = Like.objects.filter(user=user)
            likes_count = likes.count()
            if likes_count > 0:
                likes.delete()
        except Exception:
            pass
        
        # 3. Delete reviews data
        try:
            from destinations.models import Review
            reviews = Review.objects.filter(user=user)
            reviews_count = reviews.count()
            if reviews_count > 0:
                reviews.delete()
        except Exception:
            pass
            
        # 4. Delete community posts and comments
        try:
            from community.models import Post, Comment
            # Delete comments
            comments = Comment.objects.filter(author=user)
            comments_count = comments.count()
            if comments_count > 0:
                comments.delete()
            
            # Delete posts
            posts = Post.objects.filter(author=user)
            posts_count = posts.count()
            if posts_count > 0:
                posts.delete()
        except Exception:
            pass
            
        # 5. Delete planner data
        try:
            from planner.models import Planner
            planners = Planner.objects.filter(user=user)
            planners_count = planners.count()
            if planners_count > 0:
                planners.delete()
        except Exception:
            pass
        
        # 6. Final check before deleting user - check for remaining references in DB
        tables_to_check = [
            ('mypage_userprofile', 'user_id'),
            ('destinations_like', 'user_id'),
            ('destinations_review', 'user_id'),
            ('community_post', 'author_id'),
            ('community_comment', 'author_id'),
            ('planner_planner', 'user_id')
        ]
        
        with connection.cursor() as cursor:
            for table, field in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {field} = %s", [user_id])
                    count = cursor.fetchone()[0]
                    if count > 0:
                        cursor.execute(f"DELETE FROM {table} WHERE {field} = %s", [user_id])
                except Exception:
                    pass
        
        # 7. Delete user account
        user.delete()
        
        # 8. Initialize session and cookies (handled by frontend)
        response_data = {
            "message": "Account deleted successfully",
            "clear_session": True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile_by_username(request, username):
    """
    API to retrieve profile information of any user by username.
    This allows users to view other users' profiles.
    
    Parameters:
        request: HTTP request
        username: The username of the user whose profile to retrieve
        
    Returns:
        Response with user profile data
    """
    try:
        # Find user
        user = get_object_or_404(CustomUser, username=username)
        
        # Get user profile
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # If no profile, return default response
            return Response({
                "username": user.username,
                "gender": user.get_gender_display() if user.gender else None,
                "age": user.get_age_group_display() if user.age_group else None,
                "date_joined": user.date_joined,
            }, status=status.HTTP_200_OK)
        
        # If profile exists, return profile response
        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        return Response({"error": "현재 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not new_password:
        return Response({"error": "새 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not confirm_password:
        return Response({"error": "새 비밀번호 확인을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify current password
    if not user.check_password(old_password):
        return Response({"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify new password matches confirmation
    if new_password != confirm_password:
        return Response({"error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Password length validation
    if len(new_password) < 8:
        return Response({"error": "비밀번호는 최소 8자 이상이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    try:
        user.set_password(new_password)
        user.save()
        
        # Update session authentication hash to maintain login state
        update_session_auth_hash(request, user)
        
        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

