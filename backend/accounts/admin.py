from django.contrib import admin
from accounts.models import CustomUser

# Register CustomUser model to be manageable in Django Admin
admin.site.register(CustomUser)
