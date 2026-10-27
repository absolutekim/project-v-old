from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

# Set up the router for viewsets
router = DefaultRouter()
router.register(r'likes', views.LikeViewSet, basename='like') # ✅ Added API path for likes
router.register(r'reviews', views.ReviewViewSet, basename='review') # ✅ Added API path for reviews

urlpatterns = [
    # Basic location endpoints
    path('', views.get_locations, name='get_locations'), # ✅ Added API path for get locations
    path('<int:pk>/', views.get_location_detail, name='get_location_detail'), # ✅ Added API path for get location detail
    path('tag/<str:tag>/', views.get_locations_by_tag, name='get_locations_by_tag'), # ✅ Added API path for get locations by tag
    path('search/nlp/', views.search_destinations_nlp, name='search_destinations_nlp'), # ✅ Added API path for search destinations by NLP
    
    # Likes and reviews endpoints
    path('', include(router.urls)), # ✅ Added API path for likes and reviews
    path('recommend/', views.recommend_destinations, name='recommend_destinations'), # ✅ Added API path for recommend destinations
    path('user/likes/', views.UserLikesView.as_view(), name='user-likes'), # ✅ Added API path for user likes
    path('user/reviews/', views.UserReviewsView.as_view(), name='user-reviews'), # ✅ Added API path for user reviews
    path('<int:location_id>/reviews/', views.location_reviews, name='location_reviews'), # ✅ Added API path for location reviews
    
    # Popular locations endpoints
    path('most-loved/', views.most_loved_locations, name='most-loved-locations'), # ✅ Added API path for most loved locations
    
    # Location-based endpoints
    path('nearby/', views.nearby_locations, name='nearby-locations'), # ✅ Added API path for nearby locations
]