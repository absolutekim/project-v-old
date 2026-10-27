from django.contrib import admin
from .models import Location, Like, Review

# Register Location model with admin customization
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'country')  # Fields displayed in list view
    search_fields = ('name', 'description', 'category', 'city', 'country')  # Enable search by these fields
    list_filter = ('category', 'country')  # Add filters for these fields

# Register Like model with admin customization
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')  # Fields displayed in list view
    list_filter = ('created_at',)  # Add date filter
    search_fields = ('user__username', 'location__name')  # Enable search by user and location
    date_hierarchy = 'created_at'  # Add date navigation hierarchy

# Register Review model with admin customization
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'rating', 'sentiment', 'created_at')  # Fields displayed in list view
    list_filter = ('rating', 'sentiment', 'created_at')  # Add filters for rating, sentiment and date
    search_fields = ('user__username', 'location__name', 'content')  # Enable search by user, location and content
    date_hierarchy = 'created_at'  # Add date navigation hierarchy
    readonly_fields = ('sentiment', 'sentiment_score', 'keywords')  # These fields are auto-generated and read-only