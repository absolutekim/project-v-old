from django.core.management.base import BaseCommand
from django.db.models import Count
from destinations.models import Location

class Command(BaseCommand):
    help = 'Update the likes_count field of the Location model based on existing like data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to update likes_count...'))
        
        # Reset all locations' likes_count to 0
        Location.objects.all().update(likes_count=0)
        self.stdout.write('All locations have been reset to 0 likes_count.')
        
        # Calculate the likes_count for each location
        locations_with_counts = Location.objects.annotate(count=Count('likes'))
        
        # Update counter
        updated = 0
        
        # Update the likes_count field for each location
        for location in locations_with_counts:
            # Check for outliers and log them
            if location.count > 100:  # More than 100 likes are suspicious
                self.stdout.write(self.style.WARNING(
                    f'Warning: {location.name}(ID: {location.id}) has an unusually high number of likes: {location.count}'
                ))
            
            location.likes_count = location.count
            location.save(update_fields=['likes_count'])
            updated += 1
            
            # Output progress (every 100 locations)
            if updated % 100 == 0:
                self.stdout.write(f"{updated} locations updated...")
        
        self.stdout.write(self.style.SUCCESS(f"Total {updated} locations have been updated.")) 