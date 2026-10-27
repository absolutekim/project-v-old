from django.contrib import admin
from .models import Planner, PlannerItem

# Inline admin for showing PlannerItems inside Planner admin
class PlannerItemInline(admin.TabularInline):
    """
    Tabular inline view for PlannerItems.
    Allows managing destination items directly within a Planner's admin page.
    """
    model = PlannerItem
    extra = 0  # Don't show any empty forms by default

# Admin configuration for the Planner model
@admin.register(Planner)
class PlannerAdmin(admin.ModelAdmin):
    """
    Admin interface for the Planner model.
    Provides list display, filtering, search, and inline editing of planner items.
    """
    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')  # Fields to display in the list view
    list_filter = ('created_at', 'updated_at')  # Enable filtering by dates
    search_fields = ('title', 'description', 'user__username')  # Enable search by these fields
    inlines = [PlannerItemInline]  # Show planner items within the planner admin

# Admin configuration for the PlannerItem model
@admin.register(PlannerItem)
class PlannerItemAdmin(admin.ModelAdmin):
    """
    Admin interface for the PlannerItem model.
    Provides list display, filtering, and search for destination items.
    """
    list_display = ('id', 'planner', 'location', 'order', 'created_at')  # Fields to display in the list view
    list_filter = ('created_at',)  # Enable filtering by creation date
    search_fields = ('planner__title', 'location__name', 'notes')  # Enable search by these fields
