from rest_framework import serializers
from .models import Planner, PlannerItem
from destinations.serializers import LocationSerializer
from destinations.models import Location

class PlannerItemSerializer(serializers.ModelSerializer):
    """
    Serializer for planner items with detailed location information.
    Used for retrieving complete information about items in a planner.
    """
    location_details = LocationSerializer(source='location', read_only=True)  # Include full location details
    
    class Meta:
        model = PlannerItem
        fields = ['id', 'planner', 'location', 'location_details', 'order', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class PlannerSerializer(serializers.ModelSerializer):
    """
    Serializer for planners with nested items.
    Used for detailed planner views including all destination items.
    """
    items = PlannerItemSerializer(many=True, read_only=True)  # Include all items in the planner
    user = serializers.ReadOnlyField(source='user.username')  # Username of the planner owner
    
    class Meta:
        model = Planner
        fields = ['id', 'user', 'title', 'description', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class PlannerItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating planner items.
    Includes validation to limit the number of items per planner.
    """
    class Meta:
        model = PlannerItem
        fields = ['planner', 'location', 'order', 'notes']
    
    def validate(self, data):
        """
        Validate planner item data.
        Ensures a planner doesn't exceed the maximum allowed destinations (10).
        """
        planner = data.get('planner')
        if planner.items.count() >= 10:
            raise serializers.ValidationError("A planner can have a maximum of 10 destinations.")
        return data

class PlannerListSerializer(serializers.ModelSerializer):
    """
    Serializer for planner list views.
    
    Provides summary information including the count of items in each planner.
    Used for displaying planners in list format with minimal information for overview purposes.
    Does not include the full detailed items data to improve performance.
    """
    items_count = serializers.SerializerMethodField()  # Calculate number of destinations in the planner
    
    class Meta:
        model = Planner
        fields = ['id', 'title', 'description', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """
        Get the number of destinations in the planner.
        
        Parameters:
            obj: Planner instance
            
        Returns:
            int: Count of destinations in the planner
        """
        return obj.items.count()





