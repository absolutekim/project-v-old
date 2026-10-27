from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from destinations.models import Location, Like, Review
from destinations.serializers import (
    LocationSerializer, LocationDetailSerializer, 
    LikeSerializer, ReviewSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, get_object_or_404
import json
from rest_framework.permissions import AllowAny
from rest_framework import status
import urllib.parse
from django.db import connection
from .nlp_utils import nlp_processor
from .review_utils import find_similar_destinations
from collections import Counter
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db import models
import time
import random  # Adding random module for randomness
from django.db.models import Count
import math

# This class has created at earlier phase 
# but now it's not being used and replaced with others. but to avoid corruption, it's being kept.
class LocationListView(generics.ListAPIView):
    """
    API view for listing all travel destinations.
    Provides paginated access to all destinations in the database.
    
    GET: Returns a list of destinations with basic information
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]  # Anyone can view this

# This class has created at earlier phase 
# but now it's not being used and replaced with others. but to avoid corruption, it's being kept.
class LocationDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving detailed information about a specific destination.
    Provides comprehensive data about a single travel destination.
    
    GET: Returns detailed information for a single destination
    """
    queryset = Location.objects.all()
    serializer_class = LocationDetailSerializer
    permission_classes = [AllowAny]  # Anyone can view this
    
    def get_serializer_context(self):
        """
        Add request to serializer context for user-specific information.
        Allows the serializer to customize the response based on the user.
        
        Returns:
            dict: Context dictionary containing the request
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations(request):
    """
    API endpoint to retrieve all travel destinations.
    Provides a simple way to access all destinations without pagination.
    
    Parameters:
        request: HTTP request
        
    Returns:
        Response with complete list of destinations
    """
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_location_detail(request, pk):
    """
    API endpoint to retrieve detailed information for a specific destination.
    Provides comprehensive data about a single travel destination by ID.
    
    Parameters:
        request: HTTP request
        pk: Primary key of the destination to retrieve
        
    Returns:
        Response with detailed information for the specified destination or error message
    """
    try:
        location = Location.objects.get(pk=pk)
        serializer = LocationDetailSerializer(location, context={'request': request})
        return Response(serializer.data)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations_by_tag(request, tag):
    """
    API to retrieve destinations that match a specific tag (subcategory0).
    Performs sophisticated tag matching with fuzzy search capabilities.
    
    Parameters:
        request: HTTP request
        tag: URL-encoded tag string to search for
        
    Returns:
        Response with list of destinations matching the specified tag or error details
    """
    try:
        # URL decoding
        decoded_tag = urllib.parse.unquote(tag)
        print(f"Tag search: {decoded_tag}")
        
        # Search for destinations based on exact subcategory0
        with connection.cursor() as cursor:
            # Get list of valid subcategory0
            cursor.execute("""
                SELECT DISTINCT json_extract(subcategories, '$[0]') AS first_subcategory
                FROM destinations_location
                WHERE json_extract(subcategories, '$[0]') IS NOT NULL
                ORDER BY first_subcategory;
            """)
            valid_tags = [row[0] for row in cursor.fetchall() if row[0]]
            
            # Debug: print all valid tags
            print("List of valid tags:")
            for i, vtag in enumerate(valid_tags):
                print(f"{i+1}. {vtag}")
            
            # Normalize tag name (handle special characters)
            normalized_tag = None
            
            # Find exact matching tag
            if decoded_tag in valid_tags:
                normalized_tag = decoded_tag
            else:
                # Compare ignoring case
                for valid_tag in valid_tags:
                    if valid_tag.lower() == decoded_tag.lower():
                        normalized_tag = valid_tag
                        break
                
                # Compare handling special characters
                if not normalized_tag:
                    for valid_tag in valid_tags:
                        # Convert '&' and 'and' for comparison
                        if valid_tag.replace('&', 'and').lower() == decoded_tag.lower() or \
                           decoded_tag.replace('and', '&').lower() == valid_tag.lower():
                            normalized_tag = valid_tag
                            break
            
            if not normalized_tag:
                print(f"Invalid tag: {decoded_tag}")
                
                # Find most similar tag (partial match)
                similar_tags = []
                for valid_tag in valid_tags:
                    if decoded_tag.lower() in valid_tag.lower() or valid_tag.lower() in decoded_tag.lower():
                        similar_tags.append(valid_tag)
                
                if similar_tags:
                    print(f"Similar tags: {similar_tags}")
                    normalized_tag = similar_tags[0]  # Use first similar tag
                else:
                    return Response({"error": f"Invalid tag: {decoded_tag}"}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Normalized tag: {normalized_tag}")
            
            # Find locations where first subcategory matches the tag
            cursor.execute("""
                SELECT id, name
                FROM destinations_location
                WHERE json_extract(subcategories, '$[0]') = %s
                LIMIT 20
            """, [normalized_tag])
            
            matching_rows = cursor.fetchall()
            matching_ids = [row[0] for row in matching_rows]
            
            print(f"Found {len(matching_ids)} destinations with first subcategory '{normalized_tag}'")
            for row in matching_rows[:5]:  # Print first 5 only
                print(f"Matching destination - ID: {row[0]}, Name: {row[1]}")
        
        if not matching_ids:
            print(f"No destinations found for tag '{normalized_tag}'")
            return Response({"tag": decoded_tag, "destinations": []}, status=status.HTTP_200_OK)
        
        # Get matching destinations
        locations = Location.objects.filter(id__in=matching_ids)
        serializer = LocationSerializer(locations, many=True)
        
        return Response({
            "tag": decoded_tag,
            "destinations": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error during tag search: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_destinations_nlp(request):
    """
    Destination search API using sentiment analysis and natural language processing.
    Performs sophisticated text search with semantic understanding capabilities.
    
    Parameters:
        request: HTTP request with query parameters:
            - query: search term
            - limit: number of results to return (default: 20, max: 200)
            - retry: retry flag (if True, ignore cache and search again)
        
    Returns:
        Response with search results matching the query or error details
    """
    try:
        query = request.query_params.get('query', '')
        if not query:
            return Response({"error": "Please enter a search term."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process limit parameter
        try:
            limit = int(request.query_params.get('limit', 20))
            # Limit to minimum 5, maximum 200
            limit = max(5, min(limit, 200))
        except ValueError:
            limit = 20
            
        # Check retry flag
        retry = request.query_params.get('retry', 'false').lower() == 'true'
        
        print(f"NLP search query: {query}, result limit: {limit}, retry: {retry}")
        
        # Get all destinations
        all_locations = Location.objects.all()
        
        # Perform NLP search (ignore cache if retry)
        if retry:
            # Create cache key
            cache_key = f"{query}:{limit}"
            # Remove key from cache
            from .nlp_utils import search_cache
            if search_cache.get(cache_key):
                search_cache.cache.pop(cache_key, None)
                search_cache.timestamps.pop(cache_key, None)
                print(f"Cache item removed: {cache_key}")
        
        # Perform NLP search
        search_results = nlp_processor.search_destinations(query, all_locations, top_n=limit)
        
        # Format results
        formatted_results = []
        for location, similarity in search_results:
            formatted_results.append({
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "category": location.category,
                "subcategories": location.subcategories,
                "subtypes": location.subtypes,
                "image": location.image,
                "city": location.city,
                "country": location.country,
                "similarity_score": float(similarity)  # Convert numpy float to Python float
            })
        
        return Response({
            "query": query,
            "limit": limit,
            "results_count": len(formatted_results),
            "results": formatted_results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"Error during NLP search: {str(e)}")
        return Response(
            {"error": f"An error occurred during search: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Like API
class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing destination likes.
    Handles creating likes, retrieving user's likes, and unliking destinations.
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only likes belonging to the current user.
        This ensures users can only access their own like data.
        
        Returns:
            QuerySet: Filtered likes belonging to the current user
        """
        return Like.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle like creation with duplicate checks.
        Prevents users from liking the same destination multiple times.
        
        Parameters:
            request: HTTP request containing like data
            
        Returns:
            Response with created like data or conflict error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Return 409 Conflict if already liked
        location = serializer.validated_data['location']
        if Like.objects.filter(user=request.user, location=location).exists():
            return Response(
                {"detail": "You have already liked this destination."},
                status=status.HTTP_409_CONFLICT
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['delete'])
    def unlike(self, request):
        """
        Custom action to unlike a destination.
        Removes a like for a specific location.
        
        Parameters:
            request: HTTP request with location_id parameter
            
        Returns:
            Response with success status or error details
        """
        location_id = request.query_params.get('location_id')
        if not location_id:
            return Response(
                {"detail": "location_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        like = get_object_or_404(Like, user=request.user, location_id=location_id)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Review API
class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing destination reviews.
    Handles creating, retrieving, updating and deleting reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only reviews belonging to the current user.
        This ensures users can only access their own review data.
        
        Returns:
            QuerySet: Filtered reviews belonging to the current user
        """
        return Review.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle review creation with validation.
        Validates review data and prevents duplicate reviews.
        
        Parameters:
            request: HTTP request containing review data
            
        Returns:
            Response with created review data or error details
        """
        print("Review creation request received:", request.data)
        
        # Validate request data
        location_id = request.data.get('location_id')
        rating = request.data.get('rating')
        content = request.data.get('content')
        
        print(f"Location ID: {location_id}, Rating: {rating}, Content: {content}")
        
        if not location_id:
            return Response({"location_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # location_id is an integer or not  
            location_id = int(location_id)
        except (ValueError, TypeError):
            return Response({"location_id": ["Enter a valid integer."]}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response({"error": "rating must be a number between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not content or not content.strip():
            return Response({"error": "content is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if location exists
            location = get_object_or_404(Location, id=location_id)
            
            # Check if user already reviewed this location
            if Review.objects.filter(user=request.user, location=location).exists():
                return Response(
                    {"error": "You have already reviewed this destination."}, 
                    status=status.HTTP_409_CONFLICT
                )
            
            # Analyze review text with improved analysis
            from .review_utils import analyze_review
            try:
                analysis_result = analyze_review(content, rating=float(rating))
            except Exception as e:
                print(f"Analysis error occurred: {str(e)}")
                # Use default values if analysis fails
                analysis_result = {
                    'sentiment': 'POSITIVE' if rating >= 4 else ('NEGATIVE' if rating <= 2 else 'NEUTRAL'),
                    'sentiment_score': 0.5,
                    'positive_keywords': [],
                    'negative_keywords': [],
                    'meaning_units': {
                        'phrases': [],
                        'adj_noun_pairs': [],
                        'negation_concepts': [],
                        'positive_units': [],
                        'negative_units': []
                    }
                }
            
            # Prepare keyword data in a new way
            # 1. Use only basic data that can be JSON serialized
            # 2. Do not store dictionary strings, let the model serialize
            keywords_data = {
                'positive': analysis_result.get('positive_keywords', []),
                'negative': analysis_result.get('negative_keywords', []),
                # Meaning units are simplified
                'phrases': analysis_result.get('meaning_units', {}).get('phrases', []),
                'adj_noun_pairs': analysis_result.get('meaning_units', {}).get('adj_noun_pairs', []),
                'sentiment': analysis_result.get('sentiment', 'NEUTRAL')
            }
            
            # Instead of directly creating the model, use the serializer
            review_data = {
                'user': request.user.id,
                'location_id': location.id,
                'content': content,
                'rating': rating,
                'sentiment': analysis_result.get('sentiment', 'NEUTRAL'),
                'keywords': keywords_data  # simple structure
            }
            
            serializer = self.get_serializer(data=review_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # save data through serializer
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Destination recommendation API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_destinations(request):
    """
    Personalized destination recommendation API.
    Recommends destinations based on user's likes, reviews, selected tags, and recently viewed destinations.
    Uses sophisticated recommendation algorithm with multiple ranking factors.
    
    Parameters:
        request: HTTP POST request with optional recently_viewed list and query parameters:
            - limit: Maximum number of recommendations to return (default: 10)
    
    Returns:
        Response with various categories of recommendations:
            - results: Main recommendation list
            - keyword_recommendations: Based on review keywords
            - subcategory_recommendations: Based on preferred subcategories
            - subtype_recommendations: Based on preferred subtypes
            - country_recommendations: Based on preferred countries
            - recently_viewed_recommendations: Based on recently viewed items
            - tag_group_recommendations: Grouped by user's selected tags
    """
    user = request.user
    limit = int(request.query_params.get('limit', 10))
    
    # Set random seed based on current time
    random.seed(time.time())
    
    print(f"Starting personalized recommendations for user {user.username} - timestamp: {time.time()}")
    
    # 1. Collect user activity data
    likes = Like.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    
    likes_count = likes.count()
    reviews_count = reviews.count()
    total_activities = likes_count + reviews_count
    
    print(f"User activity: {likes_count} likes, {reviews_count} reviews")
    
    # Get recently viewed destinations
    recently_viewed = request.data.get('recently_viewed', [])
    has_recently_viewed = len(recently_viewed) > 0
    
    if has_recently_viewed:
        print(f"Number of recently viewed destinations: {len(recently_viewed)}")
    
    # Print liked destination IDs (debugging)
    liked_location_ids = [like.location.id for like in likes]
    print(f"Liked destination IDs: {liked_location_ids}")
    
    # 2. Determine recommendation ratios based on activity data (less tag dependency with more activity)
    # If user has 10 or more activities, tag-based recommendation is minimal
    activity_weight = min(total_activities / 10, 1.0)
    tag_weight = 1.0 - activity_weight
    
    print(f"Recommendation weights: activity-based {activity_weight:.2f}, tag-based {tag_weight:.2f}")
    
    results = []
    
    # 3. Tag-based recommendations (based on tags selected during registration)
    # New users with no activity get tag-based recommendations as priority
    if total_activities == 0:
        try:
            selected_tags = user.selected_tags or []
        except:
            selected_tags = []
        
        if selected_tags:
            print(f"New user tag-based recommendations: {selected_tags}")
            
            # Search and group destinations by tag
            tag_based_results = []
            tag_groups = {}  # Group destinations by tag
            
            for tag in selected_tags:
                # Get all destinations
                all_locations = Location.objects.all()
                tag_locations = []
                
                for loc in all_locations:
                    if loc.subcategories:
                        # If it's a string, convert to list
                        subcats = loc.subcategories
                        if isinstance(subcats, str):
                            try:
                                import json
                                subcats = json.loads(subcats)
                            except:
                                subcats = [subcats]
                        
                        # If it's not a list, convert to list
                        if not isinstance(subcats, list):
                            subcats = [subcats]
                        
                        # Check if subcategories[0] exactly matches the tag
                        if subcats and len(subcats) > 0 and subcats[0] == tag:
                            tag_locations.append(loc)
                
                # Remove duplicates
                tag_locations = list({loc.id: loc for loc in tag_locations}.values())
                
                # Exclude already liked destinations
                liked_ids = [like.location.id for like in likes]
                tag_locations = [loc for loc in tag_locations if loc.id not in liked_ids]
                
                # Add tag group only if there are results
                if tag_locations:
                    # Assign similarity score to each destination (fixed at 0.7)
                    tag_group_results = [(loc, 0.7) for loc in tag_locations[:5]]
                    tag_groups[tag] = tag_group_results
                    
                    # Add to overall results list
                    tag_based_results.extend(tag_group_results)
                    
                    print(f"Found {len(tag_locations)} destinations related to tag '{tag}'")
                else:
                    print(f"No destinations found matching tag '{tag}'")
            
            # Remove duplicates
            seen_ids = set()
            unique_tag_results = []
            
            for loc, score in tag_based_results:
                if loc.id not in seen_ids:
                    seen_ids.add(loc.id)
                    unique_tag_results.append((loc, score))
            
            # Add tag-based recommendation results
            for location, similarity in unique_tag_results[:limit]:
                results.append((location, similarity))
            
            # Create tag group results
            tag_group_recommendations = {}
            for tag, group_results in tag_groups.items():
                tag_group_recommendations[tag] = []
                for location, similarity in group_results:
                    tag_group_recommendations[tag].append((location, similarity))
            
            print(f"Tag-based recommendation results: {len(results)}, Tag groups: {len(tag_group_recommendations)}")
    
    # 4. Activity-based recommendations (from likes and reviews analysis)
    if total_activities > 0:
        # 3.1 Analyze liked destinations
        liked_locations = [like.location for like in likes]
        liked_categories = Counter()
        liked_subcategories = Counter()
        liked_subtypes = Counter()
        liked_countries = Counter()
        liked_cities = Counter()
        
        for loc in liked_locations:
            if loc.category:
                liked_categories[loc.category] += 1
            
            # Analyze subcategories
            if loc.subcategories:
                if isinstance(loc.subcategories, list):
                    for subcat in loc.subcategories:
                        liked_subcategories[subcat] += 1
                elif isinstance(loc.subcategories, str):
                    liked_subcategories[loc.subcategories] += 1
            
            # Analyze subtypes
            if loc.subtypes:
                if isinstance(loc.subtypes, list):
                    for subtype in loc.subtypes:
                        liked_subtypes[subtype] += 1
                elif isinstance(loc.subtypes, str):
                    liked_subtypes[loc.subtypes] += 1
            
            if loc.country:
                liked_countries[loc.country] += 1
            if loc.city:
                liked_cities[loc.city] += 1
        
        # 3.2 Analyze reviews with improved keyword handling
        review_keywords_positive = []
        review_keywords_negative = []
        positive_reviews = []
        negative_reviews = []
        
        # List of destination IDs with high/low ratings 
        high_rated_location_ids = []  # IDs of destinations rated 4-5
        low_rated_location_ids = []   # IDs of destinations rated 1-2
        
        # Improved country extraction: Track countries mentioned in reviews
        review_countries = Counter()
        
        for review in reviews:
            # Extract keywords with context
            if hasattr(review, 'keywords'):
                # Legacy support for old reviews without separate positive/negative keywords
                if isinstance(review.keywords, list):
                    if review.rating >= 4:
                        review_keywords_positive.extend(review.keywords)
                    elif review.rating <= 2:
                        review_keywords_negative.extend(review.keywords)
                # Support for newer structure
                elif isinstance(review.keywords, dict):
                    pos_keywords = review.keywords.get('positive_keywords', [])
                    neg_keywords = review.keywords.get('negative_keywords', [])
                    if pos_keywords:
                        review_keywords_positive.extend(pos_keywords)
                    if neg_keywords:
                        review_keywords_negative.extend(neg_keywords)
                    
                    # Improved country extraction: Find country names in keywords
                    all_keywords = pos_keywords + neg_keywords
                    countries = extract_countries_from_keywords(all_keywords)
                    for country in countries:
                        review_countries[country] += 1
            
            # Improved country extraction: Extract country names directly from review content
            if hasattr(review, 'content') and review.content:
                content_countries = extract_countries_from_text(review.content)
                for country in content_countries:
                    review_countries[country] += 2  # Higher weight for explicitly mentioned countries
            
            # Improved country extraction: Add the country of the reviewed location
            if review.location.country:
                review_countries[review.location.country] += 3  # Highest weight for the country of the reviewed location
            
            # Classify by rating
            if review.rating >= 4:
                high_rated_location_ids.append(review.location.id)
                positive_reviews.append(review)
            elif review.rating <= 2:
                low_rated_location_ids.append(review.location.id)
                negative_reviews.append(review)
            # For rating 3, classify based on sentiment analysis
            elif hasattr(review, 'sentiment') and review.sentiment == 'POSITIVE':
                positive_reviews.append(review)
        
        print(f"High-rated (4-5 stars) destination IDs: {high_rated_location_ids}")
        print(f"Low-rated (1-2 stars) destination IDs: {low_rated_location_ids}")
        print(f"Positive keywords from reviews: {review_keywords_positive}")
        print(f"Negative keywords from reviews: {review_keywords_negative}")
        
        # 3.3 Calculate keyword frequency
        pos_keyword_counts = Counter(review_keywords_positive)
        neg_keyword_counts = Counter(review_keywords_negative)
        top_pos_keywords = [word for word, count in pos_keyword_counts.most_common(10)]
        top_neg_keywords = [word for word, count in neg_keyword_counts.most_common(10)]
        
        print(f"Top positive keywords: {top_pos_keywords}")
        print(f"Top negative keywords: {top_neg_keywords}")
        
        # 3.4 Find activity-based recommendation destinations
        # Search for similar destinations based on liked destination characteristics and positive review keywords
        # while avoiding destinations similar to negative review keywords
        activity_based_results = []
        
        # 3.4.1 Keyword-based search with avoid keywords
        if top_pos_keywords or top_neg_keywords:
            print(f"Top positive keywords: {top_pos_keywords}")
            print(f"Top negative keywords to avoid: {top_neg_keywords}")
            
            # add log message for adverb filtering
            common_adverbs = {
                'actually', 'quite', 'rather', 'really', 'very', 'extremely', 
                'supposedly', 'basically', 'literally', 'definitely', 'certainly',
                'absolutely', 'completely', 'totally', 'utterly', 'obviously',
                'clearly', 'simply', 'just', 'generally', 'arguably'
            }
            
            filtered_neg_keywords = [word for word in top_neg_keywords if word not in common_adverbs]
            
            if len(filtered_neg_keywords) != len(top_neg_keywords):
                removed_adverbs = [word for word in top_neg_keywords if word in common_adverbs]
                print(f"Filtered out adverbs from negative keywords: {removed_adverbs}")
                print(f"Refined negative keywords: {filtered_neg_keywords}")
            
            # Use enhanced find_similar_destinations that handles avoid_keywords
            keyword_results = find_similar_destinations(
                top_pos_keywords, 
                user.id, 
                limit=10,
                exclude_location_ids=low_rated_location_ids,
                avoid_keywords=filtered_neg_keywords  # Use filtered negative keywords
            )
            
            # Store keyword-based recommendations separately
            keyword_recommendations = []
            
            # Add keyword-based recommendation results to activity-based results
            for location, similarity in keyword_results:
                activity_based_results.append((location, similarity))
                keyword_recommendations.append((location, similarity))
                print(f"Keyword-based recommendation: {location.name}, similarity: {similarity:.2f}")
        
        # 3.4.2 Subcategory-based search
        if liked_subcategories:
            top_subcategories = [subcat for subcat, _ in liked_subcategories.most_common(5)]
            print(f"Top subcategories: {top_subcategories}")
            
            # Build query for JSON field search
            subcategory_locations = []
            
            # Get all destinations and filter in Python due to database compatibility issues
            all_locations = Location.objects.all()
            
            for loc in all_locations:
                if loc.subcategories:
                    # Convert string to list if necessary
                    loc_subcats = loc.subcategories
                    if isinstance(loc_subcats, str):
                        try:
                            import json
                            loc_subcats = json.loads(loc_subcats)
                        except:
                            loc_subcats = [loc_subcats]
                    
                    # Convert to list if not a list
                    if not isinstance(loc_subcats, list):
                        loc_subcats = [loc_subcats]
                    
                    # Check for subcategory match
                    for subcat in top_subcategories:
                        if subcat in loc_subcats:
                            subcategory_locations.append(loc)
                            break
            
            # Remove duplicates
            subcategory_locations = list({loc.id: loc for loc in subcategory_locations}.values())
            
            # Exclude already liked destinations
            liked_ids = [loc.id for loc in liked_locations]
            subcategory_locations = [loc for loc in subcategory_locations if loc.id not in liked_ids]
            
            print(f"Number of subcategory-based recommendation destinations: {len(subcategory_locations)}")
            
            # Shuffle randomly to provide varied recommendations
            random.shuffle(subcategory_locations)
            
            # Select top results (varied similarity scores)
            subcategory_results = []
            for i, loc in enumerate(subcategory_locations[:limit]):
                # Similarity score - without randomness
                base_similarity = 0.75 + (i % 4) * 0.05
                similarity = base_similarity
                
                subcategory_results.append((loc, similarity))
                print(f"Subcategory-based recommendation: {loc.name}, similarity: {similarity:.2f}")
            
            activity_based_results.extend(subcategory_results)
        
        # 3.4.3 Subtype-based search
        if liked_subtypes:
            top_subtypes = [subtype for subtype, _ in liked_subtypes.most_common(5)]
            print(f"Top subtypes: {top_subtypes}")
            
            # Build query for JSON field search
            subtype_locations = []
            
            # Get all destinations and filter in Python due to database compatibility issues
            all_locations = Location.objects.all()
            
            for loc in all_locations:
                if loc.subtypes:
                    # Convert string to list if necessary
                    loc_subtypes = loc.subtypes
                    if isinstance(loc_subtypes, str):
                        try:
                            import json
                            loc_subtypes = json.loads(loc_subtypes)
                        except:
                            loc_subtypes = [loc_subtypes]
                    
                    # Convert to list if not a list
                    if not isinstance(loc_subtypes, list):
                        loc_subtypes = [loc_subtypes]
                    
                    # Check for subtype match
                    for subtype in top_subtypes:
                        # Check for exact match or partial match (inclusion)
                        if subtype in loc_subtypes or any(subtype.lower() in st.lower() for st in loc_subtypes):
                            subtype_locations.append(loc)
                            break
            
            # Remove duplicates
            subtype_locations = list({loc.id: loc for loc in subtype_locations}.values())
            
            # Exclude already liked destinations and destinations included in subcategory results
            liked_ids = [loc.id for loc in liked_locations]
            subcategory_ids = [loc[0].id for loc in subcategory_results]
            subtype_locations = [loc for loc in subtype_locations if loc.id not in liked_ids and loc.id not in subcategory_ids]
            
            print(f"Number of subtype-based recommendation destinations: {len(subtype_locations)}")
            
            # Shuffle randomly to provide varied recommendations
            random.shuffle(subtype_locations)
            
            # Select top results (varied similarity scores)
            subtype_results = []
            for i, loc in enumerate(subtype_locations[:limit]):
                # Similarity score - without randomness
                base_similarity = 0.7 + (i % 4) * 0.05
                similarity = base_similarity
                
                subtype_results.append((loc, similarity))
                print(f"Subtype-based recommendation: {loc.name}, similarity: {similarity:.2f}")
            
            activity_based_results.extend(subtype_results)
        
        # 3.4.4 Country-based search
        # Improve country selection logic: use both liked and review information
        combined_countries = Counter()
        
        # countries from liked locations
        if liked_countries:
            for country, count in liked_countries.items():
                combined_countries[country] += count
                
        # countries from reviews
        if review_countries:
            for country, count in review_countries.items():
                combined_countries[country] += count
                
        # ensure at least one country
        if not combined_countries and recently_viewed:
            # countries from recently viewed locations
            for item in recently_viewed:
                if item.get('country'):
                    combined_countries[item.get('country')] += 1
        
        if combined_countries:
            # select top 5 countries (increased from 3 to 5)
            top_countries = [country for country, _ in combined_countries.most_common(5)]
            print(f"Top countries: {top_countries}")
            
            country_locations = Location.objects.filter(country__in=top_countries)
            
            # Exclude already liked destinations and destinations included in subcategory/subtype results
            liked_ids = [loc.id for loc in liked_locations]
            
            # Create list of IDs to exclude from previous results (use empty list if variable not defined)
            previous_results_ids = []
            if 'subcategory_results' in locals() and subcategory_results:
                previous_results_ids.extend([loc[0].id for loc in subcategory_results])
            if 'subtype_results' in locals() and subtype_results:
                previous_results_ids.extend([loc[0].id for loc in subtype_results])
                
            country_locations = country_locations.exclude(id__in=liked_ids + previous_results_ids)
            
            # improve weight system: separate country results
            country_results_by_country = {}
            
            for country in top_countries:
                # filter locations for specific country
                country_specific_locations = country_locations.filter(country=country)
                country_specific_list = list(country_specific_locations)
                
                # process only if there are results
                if country_specific_list:
                    # shuffle to ensure diversity
                    random.shuffle(country_specific_list)
                    
                    # save country results (max 5 locations)
                    country_results_by_country[country] = []
                    
                    for i, loc in enumerate(country_specific_list[:5]):
                        # calculate weight: adjust base score based on mention frequency in reviews/likes
                        base_weight = 0.65
                        mention_bonus = min(0.3, combined_countries[country] * 0.05)  # bonus based on mention frequency
                        final_similarity = base_weight + mention_bonus + (i % 3) * 0.03  # add slight variation
                        
                        country_results_by_country[country].append((loc, final_similarity))
            
            # merge country results (add top items from each country alternately)
            country_results = []
            max_per_country = max(len(results) for country, results in country_results_by_country.items()) if country_results_by_country else 0
            
            for i in range(max_per_country):
                for country in top_countries:
                    if country in country_results_by_country and i < len(country_results_by_country[country]):
                        country_results.append(country_results_by_country[country][i])
            
            # limit results
            country_results = country_results[:limit]
            
            for location, similarity in country_results:
                print(f"Country-based recommendation: {location.name}, similarity: {similarity:.2f}")
            
            activity_based_results.extend(country_results)
    
    # 5. Tag-based recommendations (from existing tag selection) - supplementary for users with activity
    if tag_weight > 0.1 and len(results) < limit and total_activities > 0:
        # Get tags selected in user profile
        try:
            selected_tags = user.selected_tags or []
        except:
            selected_tags = []
        
        if selected_tags:
            print(f"User selected tags: {selected_tags}")
            
            # Search for destinations by tag
            tag_based_results = []
            
            for tag in selected_tags:
                # bring all destinations
                all_locations = Location.objects.all()
                tag_locations = []
                
                for loc in all_locations:
                    if loc.subcategories:
                        # If it's a string, convert to list
                        subcats = loc.subcategories
                        if isinstance(subcats, str):
                            try:
                                import json
                                subcats = json.loads(subcats)
                            except:
                                subcats = [subcats]
                        
                        # If it's not a list, convert to list
                        if not isinstance(subcats, list):
                            subcats = [subcats]
                        
                        # Check if subcategories[0] exactly matches the tag
                        if subcats and len(subcats) > 0 and subcats[0] == tag:
                            tag_locations.append(loc)
                
                # Exclude already liked destinations
                liked_ids = [like.location.id for like in likes]
                tag_locations = [loc for loc in tag_locations if loc.id not in liked_ids]
                
                # Add results (top 5 only)
                for loc in tag_locations[:5]:
                    tag_based_results.append((loc, 0.6))  # Lower similarity score for tag-based
                
                print(f"Found {len(tag_locations)} destinations related to tag '{tag}'")
            
            # Remove duplicates
            seen_ids = set(item.get("id") if isinstance(item, dict) else item[0].id for item in results)
            unique_tag_results = []
            
            for loc, score in tag_based_results:
                if loc.id not in seen_ids:
                    seen_ids.add(loc.id)
                    unique_tag_results.append((loc, score))
            
            # Add tag-based recommendation results
            remaining_slots = limit - len(results)
            for location, similarity in unique_tag_results[:remaining_slots]:
                results.append((location, similarity))
    
    # 6. Fill with popular destinations if not enough results
    if len(results) < limit:
        print("Supplementing recommendations with popular destinations due to insufficient results")
        
        # Popular destinations (ordered by most likes)
        popular_locations = Location.objects.annotate(
            total_likes=models.Count('likes')
        ).order_by('-total_likes')
        
        # Exclude already recommended destinations
        seen_ids = set(item["id"] for item in results)
        popular_locations = popular_locations.exclude(id__in=seen_ids)
        
        # Exclude already liked destinations
        liked_ids = [like.location.id for like in likes]
        popular_locations = popular_locations.exclude(id__in=liked_ids)
        
        # Add popular destinations
        remaining_slots = limit - len(results)
        for location in popular_locations[:remaining_slots]:
            results.append((location, 0.5))  # Medium similarity score for popular destinations
    
    # 7. Store subtype-based recommendation results separately
    subtype_recommendations = []
    if 'subtype_results' in locals() and subtype_results:
        for location, similarity in subtype_results[:limit]:
            subtype_recommendations.append((location, similarity))
    
    # 8. Store country-based recommendation results separately
    country_recommendations = []
    if 'country_results' in locals() and country_results:
        for location, similarity in country_results[:limit]:
            country_recommendations.append((location, similarity))
    
    # 9. Store subcategory-based recommendation results separately
    subcategory_recommendations = []
    if 'subcategory_results' in locals() and subcategory_results:
        for location, similarity in subcategory_results[:limit]:
            subcategory_recommendations.append((location, similarity))
            
    # 10. Recently viewed-based recommendation results
    recently_viewed_recommendations = []
    
    if has_recently_viewed:
        # Collect countries, subcategories, subtypes from recently viewed destinations
        rv_countries = []
        rv_subcategories = []
        rv_subtypes = []
        
        for item in recently_viewed:
            if item.get('country'):
                rv_countries.append(item.get('country'))
            
            if item.get('subcategories'):
                subcats = item.get('subcategories')
                if isinstance(subcats, list):
                    rv_subcategories.extend(subcats)
                else:
                    rv_subcategories.append(subcats)
            
            if item.get('subtypes'):
                subtypes = item.get('subtypes')
                if isinstance(subtypes, list):
                    rv_subtypes.extend(subtypes)
                else:
                    rv_subtypes.append(subtypes)
        
        # Remove duplicates
        rv_countries = list(set(rv_countries))
        rv_subcategories = list(set(rv_subcategories))
        rv_subtypes = list(set(rv_subtypes))
        
        print(f"Recently viewed countries: {rv_countries}")
        print(f"Recently viewed subcategories: {rv_subcategories}")
        print(f"Recently viewed subtypes: {rv_subtypes}")
        
        # Find destinations similar to recently viewed
        recently_viewed_locations = []
        
        # Get all destinations and filter in Python due to database compatibility issues
        all_locations = Location.objects.all()
        
        for loc in all_locations:
            # Exclude already liked destinations and recently viewed destinations
            if loc.id in liked_location_ids or any(rv['id'] == loc.id for rv in recently_viewed):
                continue
                
            match_score = 0  # Similarity score
            
            # 1. Check country match
            if loc.country and loc.country in rv_countries:
                match_score += 0.3
            
            # 2. Check subcategory match
            if loc.subcategories:
                loc_subcats = loc.subcategories
                if isinstance(loc_subcats, str):
                    try:
                        import json
                        loc_subcats = json.loads(loc_subcats)
                    except:
                        loc_subcats = [loc_subcats]
                
                if not isinstance(loc_subcats, list):
                    loc_subcats = [loc_subcats]
                
                for subcat in rv_subcategories:
                    if any(subcat.lower() in sc.lower() for sc in loc_subcats):
                        match_score += 0.2
                        break
            
            # 3. Check subtype match
            if loc.subtypes:
                loc_subtypes = loc.subtypes
                if isinstance(loc_subtypes, str):
                    try:
                        import json
                        loc_subtypes = json.loads(loc_subtypes)
                    except:
                        loc_subtypes = [loc_subtypes]
                
                if not isinstance(loc_subtypes, list):
                    loc_subtypes = [loc_subtypes]
                
                for subtype in rv_subtypes:
                    if any(subtype.lower() in st.lower() for st in loc_subtypes):
                        match_score += 0.2
                        break
            
            # Add only locations with similarity score >= 0.2 (at least one match)
            if match_score >= 0.2:
                # Limit similarity score to 0.7 (keep it moderate)
                match_score = min(match_score, 0.7)
                recently_viewed_locations.append((loc, match_score))
        
        # Sort by similarity score
        recently_viewed_locations.sort(key=lambda x: x[1], reverse=True)
        
        # Select top results
        recently_viewed_recommendations = recently_viewed_locations[:limit]
        
        print(f"Number of recently viewed-based recommendations: {len(recently_viewed_recommendations)}")
    
    print(f"Final recommendation results: {len(results)} destinations")
    
    # Function to convert Location object to serializable dictionary
    def location_to_dict(location, similarity, recommendation_type="general"):
        return {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "subcategories": location.subcategories,
                "subtypes": location.subtypes,
                "image": location.image,
                "city": location.city,
                "country": location.country,
                "similarity_score": float(similarity),
            "recommendation_type": recommendation_type
        }
    
    # Convert results to JSON-serializable format
    serialized_results = []
    for location, similarity in results:
        # Determine recommendation type (simple estimation)
        recommendation_type = "general"
        serialized_results.append(location_to_dict(location, similarity, recommendation_type))
    
    # Serialize tag group recommendation results
    serialized_tag_groups = {}
    if 'tag_group_recommendations' in locals() and tag_group_recommendations:
        for tag, recommendations in tag_group_recommendations.items():
            serialized_tag_groups[tag] = []
            for location, similarity in recommendations:
                serialized_tag_groups[tag].append(location_to_dict(location, similarity, "tag"))
    
    # Serialize subcategory recommendations
    serialized_subcategory_recommendations = []
    for location, similarity in subcategory_recommendations:
        serialized_subcategory_recommendations.append(location_to_dict(location, similarity, "subcategory"))
    
    # Serialize subtype recommendations
    serialized_subtype_recommendations = []
    for location, similarity in subtype_recommendations:
        serialized_subtype_recommendations.append(location_to_dict(location, similarity, "subtype"))
    
    # Serialize country recommendations
    serialized_country_recommendations = []
    for location, similarity in country_recommendations:
        serialized_country_recommendations.append(location_to_dict(location, similarity, "country"))
    
    # Serialize keyword-based recommendations
    serialized_keyword_recommendations = []
    if 'keyword_recommendations' in locals() and keyword_recommendations:
        for location, similarity in keyword_recommendations:
            serialized_keyword_recommendations.append(location_to_dict(location, similarity, "keyword"))
    
    # Serialize recently viewed-based recommendations
    serialized_recently_viewed_recommendations = []
    for location, similarity in recently_viewed_recommendations:
        serialized_recently_viewed_recommendations.append(location_to_dict(location, similarity, "recently_viewed"))
    
    return Response({
        "activity_weight": activity_weight,
        "tag_weight": tag_weight,
        "results": serialized_results,
        "keyword_recommendations": serialized_keyword_recommendations,
        "subcategory_recommendations": serialized_subcategory_recommendations,
        "subtype_recommendations": serialized_subtype_recommendations,
        "country_recommendations": serialized_country_recommendations,
        "recently_viewed_recommendations": serialized_recently_viewed_recommendations,
        "tag_group_recommendations": serialized_tag_groups
    }, status=status.HTTP_200_OK)

# Retrieve user's likes list
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_likes(request):
    """
    API endpoint to retrieve all destinations liked by the authenticated user.
    Returns a comprehensive list of liked destinations with complete location details.
    
    Parameters:
        request: HTTP GET request from authenticated user
    
    Returns:
        Response with count and list of liked destinations
    """
    likes = Like.objects.filter(user=request.user).select_related('location')
    
    # Format results
    results = []
    for like in likes:
        results.append({
            "id": like.id,
            "location": LocationSerializer(like.location).data,
            "created_at": like.created_at
        })
    
    return Response({
        "count": len(results),
        "results": results
    })

# Retrieve user's reviews list
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    """
    API endpoint to retrieve all reviews written by the authenticated user.
    Returns a comprehensive list of user reviews with complete location details.
    
    Parameters:
        request: HTTP GET request from authenticated user
    
    Returns:
        Response with count and list of user reviews
    """
    reviews = Review.objects.filter(user=request.user).select_related('location')
    
    # Format results
    results = []
    for review in reviews:
        results.append({
            "id": review.id,
            "location": LocationSerializer(review.location).data,
            "content": review.content,
            "rating": review.rating,
            "sentiment": review.sentiment,
            "keywords": review.keywords,
            "created_at": review.created_at,
            "updated_at": review.updated_at
        })
    
    return Response({
        "count": len(results),
        "results": results
    })

# Retrieve location's reviews list
@api_view(['GET'])
@permission_classes([AllowAny])
def location_reviews(request, location_id):
    """
    API endpoint to retrieve all reviews for a specific destination.
    Returns a list of reviews for public viewing, no authentication required.
    
    Parameters:
        request: HTTP GET request
        location_id: ID of the destination to get reviews for
    
    Returns:
        Response with count and list of reviews for the destination
    """
    reviews = Review.objects.filter(location_id=location_id)
    serializer = ReviewSerializer(reviews, many=True)
    
    return Response({
        "count": reviews.count(),
        "results": serializer.data
    })

class UserReviewsView(APIView):
    """
    API view for paginated access to user reviews.
    Provides a paginated list of the authenticated user's reviews.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET method to retrieve paginated list of user reviews.
        
        Parameters:
            request: HTTP GET request from authenticated user
        
        Returns:
            Paginated response with user reviews
        """
        reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(reviews, request)
        
        serializer = ReviewSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserLikesView(APIView):
    """
    API view for paginated access to user likes.
    Provides a paginated list of the authenticated user's liked destinations.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET method to retrieve paginated list of user likes.
        
        Parameters:
            request: HTTP GET request from authenticated user
        
        Returns:
            Paginated response with user likes
        """
        likes = Like.objects.filter(user=request.user).select_related('location').order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(likes, request)
        
        # Format results
        results = []
        for like in result_page:
            results.append({
                "id": like.id,
                "location": LocationSerializer(like.location).data,
                "created_at": like.created_at
            })
        
        return paginator.get_paginated_response(results)

@api_view(['GET'])
@permission_classes([AllowAny])
def most_loved_locations(request):
    """
    API endpoint to retrieve the top 10 most liked destinations.
    Returns destinations ranked by like count with additional rating information.
    
    Parameters:
        request: HTTP GET request
    
    Returns:
        Response with list of top 10 most liked destinations
    """
    # Sort locations by likes_count and select top 10
    # Using likes_count field that's already in the Location model
    locations = Location.objects.order_by('-likes_count')[:10]
    
    # Calculate additional information for each location
    result = []
    for location in locations:
        # Calculate average rating
        reviews = location.reviews.all()
        average_rating = None
        if reviews.exists():
            average_rating = sum(review.rating for review in reviews) / reviews.count()
        
        # Create location data
        location_data = LocationSerializer(location).data
        location_data['average_rating'] = average_rating
        
        result.append(location_data)
    
    return Response(result)

@api_view(['POST'])
@permission_classes([AllowAny])
def nearby_locations(request):
    """
    API endpoint to find destinations near a specified geographic location.
    Uses Haversine formula to calculate distances between coordinates.
    
    Parameters:
        request: HTTP POST request with:
            - latitude: User's latitude coordinate
            - longitude: User's longitude coordinate
            - radius: Search radius in kilometers (default: 50.0)
            - limit: Maximum number of results to return (default: 20)
    
    Returns:
        Response with list of nearby destinations sorted by distance
    """
    # User location information
    user_lat = request.data.get('latitude')
    user_lon = request.data.get('longitude')
    radius = float(request.data.get('radius', 50.0))  # Default radius 50km
    limit = int(request.data.get('limit', 20))  # Limit results (default 20)
    
    # If latitude/longitude not provided
    if user_lat is None or user_lon is None:
        return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
    except ValueError:
        return Response({"error": "Latitude and longitude must be numbers."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Haversine formula for distance calculation
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculates distance between two latitude/longitude coordinates (in km)
        
        Parameters:
            lat1, lon1: First coordinate pair
            lat2, lon2: Second coordinate pair
            
        Returns:
            Distance in kilometers
        """
        # Earth radius (km)
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Latitude, longitude differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    # Approximate distance per degree
    lat_km = 111.0
    lng_km = 111.0 * math.cos(math.radians(user_lat))
    
    # Convert radius to latitude/longitude difference (approximate filtering range)
    lat_delta = radius / lat_km
    lng_delta = radius / lng_km
    
    # Filter by approximate location (for performance optimization)
    locations = Location.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gte=user_lat - lat_delta,
        latitude__lte=user_lat + lat_delta,
        longitude__gte=user_lon - lng_delta,
        longitude__lte=user_lon + lng_delta
    )
    
    # Calculate exact distance and sort
    nearby_locations = []
    for location in locations:
        distance = haversine_distance(
            user_lat, user_lon, 
            location.latitude, location.longitude
        )
        
        if distance <= radius:
            location_data = LocationSerializer(location).data
            location_data['distance'] = round(distance, 2)  # Round to 2 decimal places
            nearby_locations.append(location_data)
    
    # Sort by distance
    nearby_locations.sort(key=lambda x: x['distance'])
    
    # Limit number of results
    nearby_locations = nearby_locations[:limit]
    
    return Response(nearby_locations)

# add new utility function for extracting countries from keywords
def extract_countries_from_keywords(keywords):
    """
    Extract countries from keyword list.
    """
    # List of common country names (stored in lowercase)
    common_countries = {
        'vietnam', 'thailand', 'japan', 'korea', 'china', 'malaysia', 'indonesia', 
        'singapore', 'philippines', 'australia', 'new zealand', 'usa', 'america', 
        'canada', 'mexico', 'brazil', 'peru', 'argentina', 'chile', 'uk', 'england', 
        'france', 'italy', 'spain', 'germany', 'netherlands', 'turkey', 'russia', 
        'india', 'egypt', 'morocco', 'south africa', 'greece', 'switzerland'
    }
    
    # Process country name variations
    country_aliases = {
        'american': 'usa',
        'british': 'uk',
        'english': 'uk',
        'french': 'france',
        'italian': 'italy',
        'spanish': 'spain',
        'german': 'germany',
        'dutch': 'netherlands',
        'turkish': 'turkey',
        'russian': 'russia',
        'indian': 'india',
        'egyptian': 'egypt',
        'thai': 'thailand',
        'vietnamese': 'vietnam',
        'japanese': 'japan',
        'south_korean': 'south_korea',
        'chinese': 'china',
        'malaysian': 'malaysia',
        'indonesian': 'indonesia'
    }
    
    found_countries = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Direct match
        if keyword_lower in common_countries:
            found_countries.append(keyword_lower)
        
        # Alias match
        elif keyword_lower in country_aliases:
            found_countries.append(country_aliases[keyword_lower])
    
    return found_countries

def extract_countries_from_text(text):
    """
    Extract countries from text.
    """
    # Include country name variations
    countries_with_variants = {
        'vietnam': ['vietnam', 'vietnamese', 'hanoi', 'ho chi minh'],
        'thailand': ['thailand', 'thai', 'bangkok', 'phuket'],
        'japan': ['japan', 'japanese', 'tokyo', 'kyoto', 'osaka'],
        'south_korea': ['south_korea', 'south_korean', 'seoul', 'busan'],
        'china': ['china', 'chinese', 'beijing', 'shanghai'],
        'malaysia': ['malaysia', 'malaysian', 'kuala lumpur', 'penang'],
        'indonesia': ['indonesia', 'indonesian', 'bali', 'jakarta'],
        'singapore': ['singapore', 'singaporean'],
        'philippines': ['philippines', 'filipino', 'manila', 'cebu'],
        'australia': ['australia', 'australian', 'sydney', 'melbourne'],
        'usa': ['usa', 'america', 'american', 'united states', 'new york', 'los angeles'],
        'uk': ['uk', 'britain', 'british', 'england', 'london'],
        'france': ['france', 'french', 'paris', 'nice'],
        'italy': ['italy', 'italian', 'rome', 'venice', 'milan'],
        'spain': ['spain', 'spanish', 'madrid', 'barcelona'],
        'germany': ['germany', 'german', 'berlin', 'munich']
    }
    
    found_countries = []
    text_lower = text.lower()
    
    for country, variants in countries_with_variants.items():
        for variant in variants:
            if variant in text_lower:
                found_countries.append(country)
                break  # Add only once if a country variant is found
    
    return found_countries
