from django.db import models
from django.conf import settings
from destinations.models import Location

class Planner(models.Model):
    """
    Travel planner created by users to organize their trip destinations.
    A planner contains multiple locations organized in a specific order.
    """
    id = models.AutoField(primary_key=True)  # Primary key for the planner
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='planners')  # User who owns this planner
    title = models.CharField(max_length=100)  # Title of the travel plan
    description = models.TextField(blank=True, null=True)  # Optional description of the travel plan
    created_at = models.DateTimeField(auto_now_add=True)  # When the planner was created
    updated_at = models.DateTimeField(auto_now=True)  # When the planner was last updated
    
    def __str__(self):
        return f"{self.user.username}'s planner: {self.title}"
    
    class Meta:
        ordering = ['-created_at']  # Order planners by creation date, newest first

class PlannerItem(models.Model):
    """
    Individual destinations added to a travel planner.
    Each item represents a location in the user's travel itinerary.
    """
    id = models.AutoField(primary_key=True)  # Primary key for the planner item
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE, related_name='items')  # Reference to the parent planner
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # The destination location
    order = models.IntegerField(default=0)  # The sequence order of destinations
    notes = models.TextField(blank=True, null=True)  # Optional notes about this destination
    created_at = models.DateTimeField(auto_now_add=True)  # When this item was added to the planner
    
    def __str__(self):
        return f"{self.planner.title} - {self.location.name} (order: {self.order})"
    
    class Meta:
        ordering = ['order']  # Order items by their sequence number
        unique_together = ['planner', 'location']  # Prevent duplicate locations in the same planner
