from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlannerViewSet, PlannerItemViewSet

# Set up automatic URL routing for ViewSets
router = DefaultRouter()
router.register(r'planners', PlannerViewSet, basename='planner')  # Endpoints for planner management
router.register(r'planner-items', PlannerItemViewSet, basename='planner-item')  # Endpoints for items within planners

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated URLs
]





