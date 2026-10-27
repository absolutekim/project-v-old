"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse  # ✅ Added JsonResponse import
from django.conf import settings
from django.conf.urls.static import static


def root(request):
    return JsonResponse({"message": "Welcome to the Django Backend!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root),  # Added root URL
    path('api/', include('api.urls')),
    path('api/accounts/', include('accounts.urls')), # ✅ Added API path for accounts app
    path('api/community/', include('community.urls')),  # ✅ Added API path for community app
    path('api/destinations/', include('destinations.urls')), # ✅ Added API path for destinations app
    path('api/mypage/', include('mypage.urls')), # ✅ Added API path for my page app
    path('api/planner/', include('planner.urls')),  # ✅ Added API path for planner app
    path('api/flights/', include('flight.urls')),  # ✅ Added API path for flight app
]

# Add media files URL pattern in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)