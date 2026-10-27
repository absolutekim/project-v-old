"""
This script updates the likes_count field in the Location model based on existing like data.
Run it in the Django shell:
python manage.py shell < destinations/update_likes_count.py
"""

from django.db.models import Count
from destinations.models import Location

def update_likes_count():
    print("Starting likes count update...")
    
    # Calculate the number of likes for each location
    locations_with_counts = Location.objects.annotate(count=Count('likes'))
    
    # Update counter
    updated = 0
    
    # Update the likes_count field for each location
    for location in locations_with_counts:
        location.likes_count = location.count
        location.save(update_fields=['likes_count'])
        updated += 1
        
        # Print progress (every 100 locations)
        if updated % 100 == 0:
            print(f"{updated} locations updated...")
    
    print(f"Likes count updated for a total of {updated} locations.")

if __name__ == "__main__":
    update_likes_count() 