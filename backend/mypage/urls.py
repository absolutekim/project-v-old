from django.urls import path
from .views import MyPageViewSet, get_user_achievements, AchievementViewSet, change_password
from rest_framework.routers import DefaultRouter

# 라우터를 사용하여 ViewSet 등록
router = DefaultRouter()
router.register(r'achievements', AchievementViewSet, basename='achievement')

# URL patterns for the mypage app
urlpatterns = [
    # Profile endpoints
    path('profile/', MyPageViewSet.as_view({
        'get': 'retrieve',  # GET request to retrieve user profile
        'put': 'update'     # PUT request to update user profile
    })),
    
    # 기존 Achievements endpoint (하위 호환성 유지)
    path('achievements-list/', get_user_achievements, name='user-achievements-list'),
    
    # Password change endpoint
    path('change-password/', change_password, name='change-password'),
]

# 라우터 URL 패턴 추가
urlpatterns += router.urls
