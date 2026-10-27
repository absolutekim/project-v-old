from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Planner, PlannerItem
from .serializers import (
    PlannerSerializer, 
    PlannerItemSerializer, 
    PlannerItemCreateSerializer,
    PlannerListSerializer
)
from destinations.models import Location

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a planner to access it.
    This ensures that users can only view and modify their own planners.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class PlannerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Planner CRUD operations.
    Provides endpoints for creating, reading, updating and deleting travel planners.
    """
    serializer_class = PlannerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Return only planners owned by the current authenticated user.
        This ensures users can only see their own planners.
        """
        return Planner.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on the request method.
        For list views, use a simplified serializer to improve performance.
        """
        if self.action == 'list':
            return PlannerListSerializer
        return PlannerSerializer
    
    def perform_create(self, serializer):
        """
        Set the current user as the owner when creating a new planner.
        This associates the planner with the authenticated user.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Custom endpoint to retrieve all items in a specific planner.
        Returns detailed information about each destination in the planner.
        
        Parameters:
            request: HTTP request
            pk: Primary key of the planner
        
        Returns:
            Response with serialized planner items
        """
        planner = self.get_object()
        items = planner.items.all()
        serializer = PlannerItemSerializer(items, many=True)
        return Response(serializer.data)

class PlannerItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PlannerItem CRUD operations.
    Provides endpoints for managing destinations within a travel planner.
    """
    serializer_class = PlannerItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only planner items from planners owned by the current user.
        This ensures users can only see items from their own planners.
        """
        return PlannerItem.objects.filter(planner__user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on the request method.
        Use a specialized serializer for create/update operations.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PlannerItemCreateSerializer
        return PlannerItemSerializer
    
    def perform_create(self, serializer):
        """
        Validate that the user owns the planner before creating a new item.
        This prevents users from adding items to other users' planners.
        
        Parameters:
            serializer: The serializer instance with validated data
        
        Returns:
            None or Response with error details
        """
        planner = serializer.validated_data.get('planner')
        
        # Check if user owns the planner
        if planner.user != self.request.user:
            return Response(
                {"detail": "You are not the owner of this planner."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Custom endpoint to reorder items within a planner.
        Allows updating the sequence of destinations in a travel itinerary.
        
        Parameters:
            request: HTTP request containing items with new order values
        
        Returns:
            Response with success message or error details
        """
        items_data = request.data.get('items', [])
        if not items_data:
            return Response(
                {"detail": "No item data provided."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify all items belong to the current user
        item_ids = [item.get('id') for item in items_data]
        items = PlannerItem.objects.filter(id__in=item_ids)
        
        if items.count() != len(item_ids):
            return Response(
                {"detail": "Some items could not be found."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for item in items:
            if item.planner.user != request.user:
                return Response(
                    {"detail": "You don't own some of these items."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Update the order of each item
        for item_data in items_data:
            item_id = item_data.get('id')
            new_order = item_data.get('order')
            
            if item_id and new_order is not None:
                PlannerItem.objects.filter(id=item_id).update(order=new_order)
        
        return Response({"detail": "Items order has been updated."}, status=status.HTTP_200_OK)
