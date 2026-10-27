from django.urls import path
from .views import get_airports, search_flights, get_flight_details, search_flights_complete

# flight urls (api)
urlpatterns = [
    path("search/", search_flights, name="search-flights"),
    path("get-airports/", get_airports, name="get-airports"),  # Airport autocomplete
    path('get-flight-details/', get_flight_details, name='get-flight-details'),
    path('get-complete-results/', search_flights_complete, name='search-flights-complete'),
] 