from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import F

User = get_user_model()

# Variable to temporarily store the location IDs liked by users
# key: user ID, value: list of location IDs liked by the user
_temp_user_liked_locations = {}

@receiver(pre_delete, sender=User)
def store_user_likes_before_delete(sender, instance, **kwargs):
    """
    Store the location IDs liked by the user before deleting the user.
    """
    try:
        # Get the list of location IDs liked by the user
        location_ids = list(instance.likes.values_list('location_id', flat=True))
        
        if location_ids:
            _temp_user_liked_locations[instance.id] = location_ids
    except Exception as e:
        pass

@receiver(post_delete, sender=User)
def update_likes_count_after_user_delete(sender, instance, **kwargs):
    """
    Update the likes count for locations liked by the user after deleting the user.
    """
    try:
        user_id = instance.id
        location_ids = _temp_user_liked_locations.pop(user_id, None)
        
        if not location_ids:
            return
            
        # Get the module from the destinations app
        from destinations.models import Location
        
        # Decrease the likes count for the locations
        for location_id in location_ids:
            try:
                location = Location.objects.get(id=location_id)
                location.likes_count = max(0, location.likes_count - 1)  # Prevent going below 0
                location.save(update_fields=['likes_count'])
            except Location.DoesNotExist:
                # If the location has already been deleted, ignore it
                pass
    except Exception as e:
        pass 