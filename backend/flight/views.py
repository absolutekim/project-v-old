from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '8f1784b2e7msh80c7600404170eep16fe6fjsn259a7a07d901')  # In production, this key should be set as an environment variable
RAPIDAPI_HOST = "sky-scanner3.p.rapidapi.com"

# API endpoints
AUTO_COMPLETE_URL = "https://sky-scanner3.p.rapidapi.com/flights/auto-complete"
SEARCH_ROUNDTRIP_URL = "https://sky-scanner3.p.rapidapi.com/flights/search-roundtrip"
SEARCH_ONEWAY_URL = "https://sky-scanner3.p.rapidapi.com/flights/search-one-way"
FLIGHT_DETAIL_URL = "https://sky-scanner3.p.rapidapi.com/flights/detail"

# default headers
DEFAULT_HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

@api_view(['GET'])
def get_airports(request):
    """Airport autocomplete API"""
    query = request.GET.get('query', '')
    
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)
    
    querystring = {"query": query}
    
    try:
        response = requests.get(AUTO_COMPLETE_URL, headers=DEFAULT_HEADERS, params=querystring)
        response.raise_for_status()  # raise an exception if an error occurs
        
        # airport autocomplete search is not logged (to avoid creating too much data)
        
        return Response(response.json())
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def search_flights(request):
    """Flight search API (round/one-way)"""
    trip_type = request.GET.get('trip_type', 'round')  # 'round' or 'one-way'
    from_entity_id = request.GET.get('fromEntityId', '')
    to_entity_id = request.GET.get('toEntityId', '')
    depart_date = request.GET.get('departDate', '')
    return_date = request.GET.get('returnDate', '')
    cabin_class = request.GET.get('cabinClass', 'economy')
    adults = request.GET.get('adults', '1')
    children = request.GET.get('children', '0')
    infants = request.GET.get('infants', '0')
    
    if not from_entity_id:
        return Response({"error": "From location is required"}, status=400)
    
    # default query parameters
    querystring = {
        "fromEntityId": from_entity_id,
        "toEntityId": to_entity_id,
        "cabinClass": cabin_class,
        "adults": adults,
        "children": children,
        "infants": infants
    }
    
    # if the departure date is provided, add it to the query parameters
    if depart_date:
        querystring["departDate"] = depart_date
    
    # if the round trip is selected and the return date is provided, add it to the query parameters
    if trip_type == 'round' and return_date:
        querystring["returnDate"] = return_date
        url = SEARCH_ROUNDTRIP_URL
    else:
        url = SEARCH_ONEWAY_URL
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, params=querystring)
        response.raise_for_status()
        
        response_data = response.json()
        
        return Response(response_data)
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def search_flights_complete(request):
    """Process subsequent requests for incomplete flight search results"""
    print("="*40)
    print("[DEBUG] search_flights_complete endpoint was called")
    print("[DEBUG] Request method:", request.method)
    print("[DEBUG] Request GET params:", dict(request.GET))
    print("="*40)
    
    session_id = request.GET.get('sessionId', '')
    
    if not session_id:
        print("[ERROR] No sessionId provided in request")
        return Response({"error": "session ID is required"}, status=400)
    
    print(f"[DEBUG] search_flights_complete called with session_id: {session_id}")
    
    # API endpoint
    api_url = "https://sky-scanner3.p.rapidapi.com/flights/search-incomplete"
    print(f"[DEBUG] Using API URL: {api_url}")
    
    # set API call parameters
    querystring = {
        "sessionId": session_id
    }
    
    # optional filter parameters
    stops = request.GET.get('stops', '')
    sort = request.GET.get('sort', '')
    airlines = request.GET.get('airlines', '')
    
    # add optional parameters only if they are provided
    if stops:
        querystring["stops"] = stops
    if sort:
        querystring["sort"] = sort
    if airlines:
        querystring["airlines"] = airlines
        
    # other optional parameters
    market = request.GET.get('market', '')
    locale = request.GET.get('locale', '')
    currency = request.GET.get('currency', '')
    cookie = request.GET.get('cookie', '')
    
    if market:
        querystring["market"] = market
    if locale:
        querystring["locale"] = locale
    if currency:
        querystring["currency"] = currency
    if cookie:
        querystring["cookie"] = cookie
    
    print(f"[DEBUG] API call parameters: {querystring}")
    
    try:
        print(f"[DEBUG] Making request to SkyScanner API...")
        
        # Make the API call
        response = requests.get(
            api_url, 
            headers=DEFAULT_HEADERS, 
            params=querystring
        )
        
        print(f"[DEBUG] API response received with status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[DEBUG] Response content: {response.text}")
        
        # Raise exception for bad responses
        response.raise_for_status()
        
        # Parse JSON response
        response_data = response.json()
        print(f"[DEBUG] API response successfully parsed to JSON")
        
        # Format the response to be consistent with search_flights
        formatted_response = {
            "status": True,
            "message": "Flight search completed successfully",
            "data": response_data
        }
        
        print("[DEBUG] Returning formatted response to client")
        return Response(formatted_response)
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"[ERROR] API request failed: {error_msg}")
        
        # Return a special error code so the frontend knows to use the initial search results
        return Response({
            "status": False,
            "message": f"SkyScanner API 호출 오류: {error_msg}",
            "data": None,
            "errorCode": "API_UNAVAILABLE"
        }, status=500)

@api_view(['GET'])
def get_flight_details(request):
    """Flight details API"""
    token = request.GET.get('token', '')
    itinerary_id = request.GET.get('itineraryId', '')
    
    if not token or not itinerary_id:
        return Response({"error": "Token and itineraryId are required"}, status=400)
    
    querystring = {
        "token": token,
        "itineraryId": itinerary_id
    }
    
    try:
        response = requests.get(FLIGHT_DETAIL_URL, headers=DEFAULT_HEADERS, params=querystring)
        response.raise_for_status()
        return Response(response.json())
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

