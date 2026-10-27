from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
import inspect
import sys

User = get_user_model()

# Check if the call stack is from RegisterSerializer
def is_called_from_register_serializer():
    stack = inspect.stack()
    for frame_info in stack:
        # Serializers.py file's create function is called
        if 'serializers.py' in frame_info.filename and 'create' in frame_info.function:
            return True
    return False

# Check if the call stack is from RegisterSerializer's user.save()
def is_password_set_save():
    stack = inspect.stack()
    serializers_in_stack = False
    set_password_in_stack = False
    
    for frame_info in stack:
        if 'serializers.py' in frame_info.filename:
            serializers_in_stack = True
        if 'set_password' in frame_info.code_context[0] if frame_info.code_context else '':
            set_password_in_stack = True
    
    # If both serializers.py and set_password are in the stack, consider it a password setting save
    return serializers_in_stack and set_password_in_stack

# Signal handler to automatically create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile instance when a new User is saved.
    This ensures every user has an associated profile from the start.
    
    Args:
        sender: The User model class
        instance: The actual User instance being saved
        created: Boolean indicating if this is a new User
    """
    # Check the call stack - Skip UserProfile creation if called from RegisterSerializer
    if created:
        # Check if the creation is from RegisterSerializer
        if is_called_from_register_serializer():
            return
        
        # Create UserProfile if not called from RegisterSerializer (e.g. Admin page)
        UserProfile.objects.create(user=instance)

# Signal handler to save the UserProfile when the User is updated
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Saves the associated UserProfile when a User instance is saved.
    If the profile doesn't exist, it creates one to ensure data consistency.
    
    Args:
        sender: The User model class
        instance: The actual User instance being saved
    """
    # 1. If the user is newly created
    if created:
        # Skip creation if called from RegisterSerializer
        if is_called_from_register_serializer():
            return
        
        return
    
    # 2. Skip if called from RegisterSerializer or password setting save
    if is_called_from_register_serializer() or is_password_set_save():
        return
        
    # 3. If it's a normal user update
    try:
        # Update the profile if it exists
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Create the profile if it doesn't exist
        UserProfile.objects.create(user=instance)

# Signal handler to ensure UserProfile is deleted when User is deleted (backup for CASCADE)
@receiver(post_delete, sender=User)
def ensure_profile_deleted(sender, instance, **kwargs):
    """
    Ensures UserProfile is deleted when User is deleted (backup for CASCADE)
    
    Args:
        sender: The User model class
        instance: The deleted User instance
    """
    from django.db import connection
    user_id = instance.id
    try:
        # Use direct SQL to handle it more reliably
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM mypage_userprofile WHERE user_id = %s", [user_id])
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute("DELETE FROM mypage_userprofile WHERE user_id = %s", [user_id])
    except Exception as e:
        pass 