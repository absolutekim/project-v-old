import re
from collections import Counter
from .nlp_utils import nlp_processor

def analyze_review(review_text, rating=None):
    """
    Analyze review text to extract sentiment and keywords.
    Now with enhanced meaning unit extraction using spaCy.
    
    Parameters:
        review_text: The review text to analyze
        rating: Optional rating value to help classify sentiment
        
    Returns:
        dict: Dictionary containing:
            - sentiment: Sentiment classification (POSITIVE, NEGATIVE, NEUTRAL)
            - sentiment_score: Confidence score of sentiment analysis (0-1)
            - positive_keywords: List of positive context keywords from the review
            - negative_keywords: List of negative context keywords from the review
            - meaning_units: Semantic meaning units extracted from the review
    """
    # Perform sentiment analysis
    sentiment, confidence = nlp_processor.analyze_sentiment(review_text)
    
    # Consider rating if provided (override sentiment analysis for clearer categorization)
    if rating is not None:
        if rating >= 4:
            sentiment = "POSITIVE"
        elif rating <= 2:
            sentiment = "NEGATIVE"
    
    # Extract keywords with context using enhanced method
    try:
        pos_keywords, neg_keywords, meaning_units = extract_contextual_keywords(review_text, sentiment)
    except Exception as e:
        print(f"Keyword extraction error: {str(e)}")
        # Initialize empty lists in case of error
        pos_keywords, neg_keywords = [], []
        meaning_units = {
            'phrases': [],
            'adj_noun_pairs': [],
            'negation_concepts': [],
            'positive_units': [],
            'negative_units': []
        }
    
    return {
        'sentiment': sentiment,
        'sentiment_score': float(confidence),
        'positive_keywords': pos_keywords,
        'negative_keywords': neg_keywords,
        'meaning_units': meaning_units
    }

def extract_contextual_keywords(text, sentiment, top_n=5):
    """
    Extract important keywords from text, separating by positive/negative context.
    Now with spaCy integration for advanced meaning unit extraction.
    
    Parameters:
        text: Text to extract keywords from
        sentiment: Sentiment classification to help separate keywords
        top_n: Number of keywords to return (default: 5)
        
    Returns:
        tuple: (positive_keywords, negative_keywords, meaning_units)
    """
    # Initialize default values (used in case of exception)
    default_positive_tokens = []
    default_negative_tokens = []
    default_meaning_units = {
        'phrases': [],
        'adj_noun_pairs': [],
        'negation_concepts': [],
        'positive_units': [],
        'negative_units': []
    }
    
    try:
        # 1. Regular keyword extraction (keep existing functionality)
        # Preprocess text with improved tokenization
        tokens = nlp_processor.preprocess_text(text, filter_adverbs=True)
        
        # Separate words by context
        negation_words = {'no', 'not', 'never', 'nothing', 'nowhere', 'none', 'neither', 'nor', 'barely', 'hardly', 'rarely', 'seldom', 'lack', 'missing', 'empty'}
        negation_context = False
        positive_tokens = []
        negative_tokens = []
        
        # Simple negation detection
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in negation_words or word.endswith("n't"):
                negation_context = True
                # Look ahead for content words (nouns, adjectives)
                for j in range(i+1, min(i+4, len(words))):
                    if j < len(words) and words[j] in tokens and words[j] not in negation_words:
                        negative_tokens.append(words[j])
        
        # Categorize remaining tokens
        for token in tokens:
            if token.lower() in negative_tokens:
                continue  # Already handled in negation context
            if token.lower() in negation_words:
                negative_tokens.append(token)
            else:
                if sentiment == "NEGATIVE":
                    negative_tokens.append(token)
                else:
                    positive_tokens.append(token)
        
        # 2. NEW: Enhanced meaning unit extraction with spaCy
        # Extract rich semantic units
        meaning_units = {}
        
        # Use spaCy to extract advanced meaning units
        spacy_units = nlp_processor.extract_meaning_units(text)
        
        # Categorize meaning units based on sentiment
        positive_meaning_units = []
        negative_meaning_units = []
        
        # Process adjective-noun pairs
        for pair in spacy_units['adj_noun_pairs']:
            if sentiment == "NEGATIVE":
                negative_meaning_units.append(pair)
            else:
                positive_meaning_units.append(pair)
        
        # Negation concepts always go to negative keywords
        negative_meaning_units.extend(spacy_units['negation_concepts'])
        
        # Store all extracted meaning units
        meaning_units = {
            'phrases': spacy_units['phrases'],
            'adj_noun_pairs': spacy_units['adj_noun_pairs'],
            'negation_concepts': spacy_units['negation_concepts'],
            'positive_units': positive_meaning_units,
            'negative_units': negative_meaning_units
        }
        
        # Enhance keywords with key meaning units
        # Add key meaning units to keywords
        for unit in spacy_units['negation_concepts']:
            if unit not in negative_tokens:
                negative_tokens.append(unit)
        
        # Special handling for certain patterns like "large but nothing"
        for key in spacy_units.get('negation_concepts', []):
            if key.startswith('empty_') or key.startswith('no_'):
                if key not in negative_tokens:
                    negative_tokens.append(key)
        
        # Remove duplicates and sort by frequency
        pos_counts = Counter(positive_tokens)
        neg_counts = Counter(negative_tokens)
        
        positive_keywords = [word for word, _ in pos_counts.most_common(top_n)]
        negative_keywords = [word for word, _ in neg_counts.most_common(top_n)]
        
        return positive_keywords, negative_keywords, meaning_units
    
    except Exception as e:
        print(f"Extraction process error: {e}")
        # Return default values in case of error
        return default_positive_tokens, default_negative_tokens, default_meaning_units

def find_similar_destinations(keywords, user_id, limit=10, exclude_location_ids=None, avoid_keywords=None):
    """
    Find similar destinations based on keywords, now with keywords to avoid.
    Uses NLP search to identify destinations matching the provided positive keywords
    and avoiding destinations matching negative keywords.
    
    Parameters:
        keywords: List of keywords to search for (positive keywords)
        user_id: User ID (used to exclude already visited/liked destinations)
        limit: Maximum number of destinations to return (default: 10)
        exclude_location_ids: List of location IDs to exclude from results
        avoid_keywords: List of keywords to avoid (negative keywords)
        
    Returns:
        list: List of tuples containing (location, similarity_score) sorted by similarity
    """
    from .models import Location, Like, Review
    
    # Return empty list if no keywords
    if not keywords and not avoid_keywords:
        return []
    
    # Filter out adverbs from avoid_keywords
    if avoid_keywords:
        # Common adverbs to remove
        common_adverbs = {
            'actually', 'quite', 'rather', 'really', 'very', 'extremely', 
            'supposedly', 'basically', 'literally', 'definitely', 'certainly',
            'absolutely', 'completely', 'totally', 'utterly', 'obviously',
            'clearly', 'simply', 'just', 'generally', 'arguably'
        }
        
        # Remove common adverbs from avoid_keywords
        avoid_keywords = [word for word in avoid_keywords if word not in common_adverbs]
        
        # Add special meaning units if available
        for i, keyword in enumerate(avoid_keywords):
            # For keywords like "large" but in negative context, replace with "empty_large"
            if keyword in ['large', 'big', 'huge', 'spacious'] and 'nothing' in avoid_keywords:
                avoid_keywords[i] = f"empty_{keyword}"
        
        print(f"Refined avoid keywords (removed adverbs): {avoid_keywords}")
    
    # Convert keywords to space-separated string
    query = ' '.join(keywords) if keywords else ""
    
    # Get all locations
    all_locations = Location.objects.all()
    
    # Get list of location IDs the user has already liked
    liked_location_ids = Like.objects.filter(user_id=user_id).values_list('location_id', flat=True)
    
    # Initialize exclude_location_ids as empty list if None
    if exclude_location_ids is None:
        exclude_location_ids = []
    
    # Perform NLP search with positive keywords
    search_results = []
    if query:
        search_results = nlp_processor.search_destinations(
            query, 
            all_locations, 
            top_n=limit*3  # Fetch more results initially to allow filtering
        )
    
    # Filter out destinations that match avoid_keywords
    if avoid_keywords and len(avoid_keywords) > 0:
        avoid_query = ' '.join(avoid_keywords)
        print(f"Avoiding destinations similar to keywords: {avoid_query}")
        
        # Find destinations to avoid
        avoid_results = nlp_processor.search_destinations(
            avoid_query,
            all_locations,
            top_n=limit*2
        )
        
        # Create a set of location IDs to avoid
        avoid_location_ids = {loc.id for loc, _ in avoid_results if _ > 0.2}  # Only exclude with similarity > 0.2
        print(f"Excluding {len(avoid_location_ids)} destinations matching negative keywords")
        
        # Add to exclude list
        exclude_location_ids.extend(avoid_location_ids)
    
    # Filter results
    filtered_results = []
    for loc, similarity in search_results:
        if loc.id not in liked_location_ids and loc.id not in exclude_location_ids:
            filtered_results.append((loc, similarity))
            
    return filtered_results[:limit] 