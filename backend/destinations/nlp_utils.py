import os
import re
from collections import Counter
import time
import functools

# Check library availability
NLP_ADVANCED = False
try:
    from transformers import pipeline
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    from sentence_transformers import SentenceTransformer, util
    NLP_ADVANCED = True
    print("Advanced NLP features have been activated.")
except ImportError:
    print("Advanced NLP libraries are not installed. Only basic search functionality is available.")

# Add spaCy availability check
SPACY_AVAILABLE = False
try:
    import spacy
    # Try to load English model
    try:
        nlp_spacy = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
        print("spaCy features have been activated with en_core_web_sm model.")
    except OSError:
        print("spaCy is installed but the English language model is not available.")
        print("To download the model, run: python -m spacy download en_core_web_sm")
except ImportError:
    print("spaCy library is not installed. Enhanced language processing will not be available.")
    print("To install spaCy, run: pip install spacy")

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    # Download NLTK data (needed on first run)
    nltk_resources = ['punkt', 'stopwords']
    for resource in nltk_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"Downloading NLTK {resource}...")
            nltk.download(resource)
    
    # Download additional resources
    try:
        nltk.download('punkt')
    except:
        pass
    
    NLTK_AVAILABLE = True
    print("NLTK features have been activated.")
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK library is not installed. Basic tokenization will be used.")

# Set model caching directory
os.environ['TRANSFORMERS_CACHE'] = './models/transformers_cache'
os.environ['TORCH_HOME'] = './models/torch_cache'

# Simple LRU cache implementation
class LRUCache:
    """
    Least Recently Used (LRU) cache implementation.
    Provides efficient caching mechanism with automatic eviction of oldest items.
    """
    def __init__(self, capacity=100):
        """
        Initialize LRU cache with specified capacity.
        
        Parameters:
            capacity: Maximum number of items to store in cache
        """
        self.cache = {}
        self.capacity = capacity
        self.timestamps = {}
    
    def get(self, key):
        """
        Retrieve item from cache by key and update its timestamp.
        
        Parameters:
            key: Cache key to look up
            
        Returns:
            Cached value or None if key not found
        """
        if key in self.cache:
            self.timestamps[key] = time.time()
            return self.cache[key]
        return None
    
    def put(self, key, value):
        """
        Store item in cache with automatic eviction of oldest items.
        
        Parameters:
            key: Cache key
            value: Value to store
        """
        if len(self.cache) >= self.capacity:
            # Remove the oldest item
            oldest_key = min(self.timestamps, key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()

# Search result cache
search_cache = LRUCache(capacity=500)

class NLPProcessor:
    """
    Natural Language Processing processor for travel destination search and analysis.
    Provides sentiment analysis, text similarity calculation, and semantic search capabilities.
    Handles graceful degradation when advanced NLP libraries are not available.
    """
    def __init__(self):
        """
        Initialize NLP processor with required models and resources.
        Models are loaded lazily on first use for better performance.
        """
        # Initialize sentiment analysis model
        self.sentiment_analyzer = None
        
        # Initialize sentence embedding model
        self.sentence_model = None
        
        # Set up stopwords
        self.stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
                              'when', 'where', 'how', 'all', 'with', 'for', 'in', 'to', 'at', 'by', 
                              'from', 'on', 'off']) if not NLTK_AVAILABLE else set(stopwords.words('english'))
        
        # Model loading flag
        self.models_loaded = False
        
        # Embedding cache
        self.embedding_cache = {}
        
        # Sentiment analysis cache
        self.sentiment_cache = {}
        
        # Performance optimization settings
        self.use_lightweight_model = True
        
        # Initialize spaCy processor if available
        self.spacy_nlp = nlp_spacy if SPACY_AVAILABLE else None
    
    def load_models(self):
        """
        Load NLP models lazily (only when needed).
        Initializes sentiment analysis and sentence embedding models if advanced NLP is available.
        
        Note:
            This method is called automatically by other methods when needed and
            only loads models once, regardless of how many times it's called.
        """
        if self.models_loaded or not NLP_ADVANCED:
            return
        
        print("Loading NLP models...")
        start_time = time.time()
        
        # Load sentiment analysis model - explicit model specification
        self.sentiment_analyzer = pipeline(
            'sentiment-analysis',
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            revision="714eb0f"
        )
        
        # Load sentence embedding model (lightweight multilingual support model)
        if self.use_lightweight_model:
            # Use a lighter model
            model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
        else:
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            
        self.sentence_model = SentenceTransformer(model_name)
        
        self.models_loaded = True
        print(f"NLP models loaded! (Time taken: {time.time() - start_time:.2f} seconds)")
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a text string.
        Uses advanced transformer-based model if available, falls back to lexicon-based approach.
        
        Parameters:
            text: Text string to analyze
            
        Returns:
            tuple: (sentiment label, confidence score)
                   sentiment label is one of: "POSITIVE", "NEGATIVE", or "NEUTRAL"
                   confidence score is a float between 0 and 1
        """
        # Check cache
        if text in self.sentiment_cache:
            return self.sentiment_cache[text]
            
        if not NLP_ADVANCED:
            # Simple sentiment analysis (keyword-based)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'fun', 'beautiful']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'hate', 'dislike', 'boring', 'ugly', 'disappointed']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                result = ("POSITIVE", 0.8)
            elif negative_count > positive_count:
                result = ("NEGATIVE", 0.8)
            else:
                result = ("NEUTRAL", 0.5)
                
            # Cache the result
            self.sentiment_cache[text] = result
            return result
        
        if not self.models_loaded:
            self.load_models()
        
        try:
            # Process short text with a simpler method
            if len(text.split()) < 5:
                text_lower = text.lower()
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'fun', 'beautiful', 'clean']
                negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'hate', 'dislike', 'boring', 'ugly', 'disappointed', 'dirty']
                
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    result = ("POSITIVE", 0.8)
                elif negative_count > positive_count:
                    result = ("NEGATIVE", 0.8)
                else:
                    # Use model
                    model_result = self.sentiment_analyzer(text)
                    result = (model_result[0]['label'], model_result[0]['score'])
            else:
                # Use model for longer text
                model_result = self.sentiment_analyzer(text)
                result = (model_result[0]['label'], model_result[0]['score'])
                
            # Cache the result
            self.sentiment_cache[text] = result
            return result
        except Exception as e:
            print(f"Error during sentiment analysis: {str(e)}")
            result = ("NEUTRAL", 0.5)
            self.sentiment_cache[text] = result
            return result
    
    def get_embedding(self, text):
        """
        Generate text embedding vector for similarity calculations.
        Uses sentence embedding models for advanced NLP, falls back to word frequency for basic processing.
        
        Parameters:
            text: Text string to embed
            
        Returns:
            numpy.ndarray or Counter: Embedding vector representation of the text
        """
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        if not NLP_ADVANCED:
            # Simple embedding alternative (based on word frequency)
            words = self.preprocess_text(text)
            word_counts = Counter(words)
            # Convert word frequencies to a vector (simple alternative)
            result = word_counts
            self.embedding_cache[text] = result
            return result
        
        if not self.models_loaded:
            self.load_models()
        
        try:
            # Always use Sentence-Transformers model for short text too
            result = self.sentence_model.encode(text, convert_to_numpy=True)
                
            # Cache the result
            self.embedding_cache[text] = result
            return result
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            result = np.zeros(384)  # Default embedding dimension (MiniLM model)
            self.embedding_cache[text] = result
            return result
    
    def calculate_similarity(self, text1, text2):
        """
        Calculate semantic similarity between two text strings.
        Uses cosine similarity with sentence embeddings for advanced NLP,
        falls back to Jaccard similarity for basic processing.
        
        Parameters:
            text1: First text string
            text2: Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not NLP_ADVANCED:
            return self.calculate_similarity_fallback(text1, text2)
        
        if not self.models_loaded:
            self.load_models()
            
        try:
            # Calculate similarity using Sentence-Transformers
            embedding1 = self.get_embedding(text1)
            embedding2 = self.get_embedding(text2)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(embedding1, embedding2)
            
            # Improve similarity scores for short queries
            if len(text1.split()) < 3:
                # Amplify similarity score for short queries
                similarity_value = float(similarity[0][0])
                
                # Log output removed (performance improvement)
                # print(f"Original similarity: {similarity_value:.4f}, Query: '{text1}', Target: '{text2[:50]}...'")
                
                # Amplify scores above 0.2 (lowered threshold)
                if similarity_value >= 0.2:
                    # Amplify up to 0.85 max, with reduced amplification ratio (2.0 -> 1.5)
                    amplified = min(similarity_value * 1.5, 0.85)
                    # print(f"Amplified similarity: {amplified:.4f}")
                    return amplified
                # Also slightly amplify scores above 0.1
                elif similarity_value >= 0.1:
                    amplified = similarity_value * 1.3
                    # print(f"Amplified similarity: {amplified:.4f}")
                    return amplified
            
            return float(similarity[0][0])  # Convert tensor to scalar value
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            # Fall back to basic similarity calculation
            return self.calculate_similarity_fallback(text1, text2)
    
    def calculate_similarity_fallback(self, text1, text2):
        """
        Fallback method for calculating text similarity using Jaccard similarity.
        Used when advanced NLP models are not available or fail.
        
        Parameters:
            text1: First text string
            text2: Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        words1 = set(self.preprocess_text(text1))
        words2 = set(self.preprocess_text(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0.0
        
        # Improve similarity scores for short queries
        if len(text1.split()) < 3:
            # Amplify similarity score for short queries
            if similarity >= 0.2:
                # Amplify up to 0.8 max
                return min(similarity * 1.5, 0.8)
        
        return similarity
    
    def extract_meaning_units(self, text):
        """
        Extract meaning units from text using spaCy's advanced NLP capabilities.
        Identifies noun phrases, adjective-noun pairs, and negation contexts.
        
        Parameters:
            text: Text to analyze
            
        Returns:
            dict: Dictionary containing:
                - phrases: List of meaningful phrases
                - adj_noun_pairs: List of adjective-noun pairs
                - negation_concepts: List of negated concepts
                - entities: List of named entities
        """
        # Check if spaCy is available
        if not SPACY_AVAILABLE or not self.spacy_nlp:
            return {
                'phrases': [],
                'adj_noun_pairs': [],
                'negation_concepts': [],
                'entities': []
            }
        
        try:
            # Process text with spaCy
            doc = self.spacy_nlp(text)
            
            # Extract noun phrases
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
            
            # Extract adjective-noun pairs
            adj_noun_pairs = []
            for token in doc:
                if token.pos_ == "NOUN" or token.pos_ == "PROPN":
                    for child in token.children:
                        if child.pos_ == "ADJ":
                            pair = f"{child.text.lower()}_{token.text.lower()}"
                            adj_noun_pairs.append(pair)
            
            # Extract negation contexts
            negation_concepts = []
            for token in doc:
                # Check for explicit negation
                if token.dep_ == "neg":
                    head = token.head
                    # Get the concept being negated
                    if head.pos_ in ["ADJ", "VERB"]:
                        concept = f"not_{head.text.lower()}"
                        # If the head has a noun object, include it
                        for child in head.children:
                            if child.dep_ in ["dobj", "attr", "pobj"] and child.pos_ == "NOUN":
                                concept = f"not_{head.text.lower()}_{child.text.lower()}"
                                break
                        negation_concepts.append(concept)
                
                # Check for implicit negation (nothing, no one, nowhere)
                if token.lemma_ in ["nothing", "nobody", "nowhere", "none"]:
                    for other_token in doc:
                        # Find related adjectives or verbs
                        if (other_token.head == token or token.head == other_token) and other_token.pos_ in ["ADJ", "VERB"]:
                            negation_concepts.append(f"no_{other_token.text.lower()}")
            
            # Identify named entities
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Create context-aware phrases for "large but nothing" type expressions
            context_aware_phrases = []
            for i, token in enumerate(doc):
                if i < len(doc) - 3 and token.pos_ == "ADJ":
                    # Check for pattern: ADJ + but + negation
                    if any(doc[i+j].text.lower() in ["but", "however", "yet", "although"] for j in range(1, 3)):
                        if any(doc[i+j].lemma_ in ["nothing", "none", "empty", "no"] for j in range(2, 5)):
                            # Found pattern like "large but nothing"
                            inverse_concept = f"empty_{token.text.lower()}"
                            context_aware_phrases.append(inverse_concept)
            
            return {
                'phrases': noun_phrases,
                'adj_noun_pairs': adj_noun_pairs,
                'negation_concepts': negation_concepts + context_aware_phrases,
                'entities': entities
            }
        
        except Exception as e:
            print(f"Error during meaning unit extraction: {str(e)}")
            return {
                'phrases': [],
                'adj_noun_pairs': [],
                'negation_concepts': [],
                'entities': []
            }
    
    def preprocess_text(self, text, filter_adverbs=False):
        """
        Preprocess text for NLP analysis with improved filtering.
        Tokenizes text, removes stopwords, and optionally filters adverbs.
        
        Parameters:
            text: Text string to preprocess
            filter_adverbs: If True, filter out common adverbs
            
        Returns:
            list: List of preprocessed tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        if NLTK_AVAILABLE:
            tokens = word_tokenize(text)
        else:
            tokens = text.split()
        
        # Common adverbs to filter out
        common_adverbs = {
            'actually', 'quite', 'rather', 'really', 'very', 'extremely', 
            'supposedly', 'basically', 'literally', 'definitely', 'certainly',
            'absolutely', 'completely', 'totally', 'utterly', 'obviously',
            'clearly', 'simply', 'just', 'generally', 'arguably'
        }
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            if len(token) > 1:  # Skip single-character tokens
                if token not in self.stop_words:  # Skip stopwords
                    if not filter_adverbs or token not in common_adverbs:  # Optionally skip adverbs
                        filtered_tokens.append(token)
        
        return filtered_tokens
    
    def search_destinations(self, query, destinations, top_n=10):
        """
        Find destinations most similar to the query.
        Performs semantic search with keyword matching.
        
        Parameters:
            query: Search query text
            destinations: List of destinations (Location objects)
            top_n: Number of results to return
            
        Returns:
            List of tuples: [(destination, similarity_score), ...] sorted by similarity score
        """
        try:
            start_time = time.time()
            print(f"NLP search query: {query}")
            print(f"NLP_ADVANCED status: {NLP_ADVANCED}")
            
            # Create cache key (query + number of results)
            cache_key = f"{query}:{top_n}"
            cached_results = search_cache.get(cache_key)
            if cached_results:
                print(f"Returning results from cache (query: {query})")
                return cached_results
            
            # Log processing approach based on query length (simplified)
            query_words_count = len(query.split())
            if query_words_count < 3:
                print(f"Short query detected ({query_words_count} words)")
            
            # Preprocess query
            query_words = set(self.preprocess_text(query))
            
            # Process all destinations (no limit)
            total_destinations = len(destinations)
            print(f"Starting to process all {total_destinations} destinations")
            
            # Initial keyword filtering to identify high-relevance destinations first
            # Always enable keyword filtering for short queries
            filtered_destinations = []
            
            # Try initial filtering at the database level
            if len(query_words) > 0:
                print("Applying keyword-based pre-filtering")
                for dest in destinations:
                    dest_text = f"{dest.name} {dest.description or ''}".lower()
                    
                    # Include city and country information in search text
                    if dest.city:
                        dest_text += f" {dest.city}".lower()
                    if dest.country:
                        dest_text += f" {dest.country}".lower()
                    
                    # Select only destinations containing at least one keyword
                    if any(word in dest_text for word in query_words):
                        filtered_destinations.append(dest)
                
                # Use the original list if there aren't enough results
                if len(filtered_destinations) < max(50, top_n * 2):  # At least 50 or 2x requested results
                    print(f"Not enough filtering results ({len(filtered_destinations)}), using original list")
                    # Use full list
                    filtered_destinations = destinations
                    print(f"Processing all {len(filtered_destinations)} destinations")
                else:
                    print(f"Filtered to {len(filtered_destinations)} destinations by keywords")
            else:
                # Use full list
                filtered_destinations = destinations
                print(f"Processing all {len(filtered_destinations)} destinations")
            
            # Start measuring processing time
            process_start_time = time.time()
            
            results = []
            for i, dest in enumerate(filtered_destinations):
                # Log progress (every 5000 items) - reduced logging frequency
                if i > 0 and i % 5000 == 0:
                    elapsed = time.time() - process_start_time
                    print(f"Progress: {i}/{len(filtered_destinations)} processed ({elapsed:.2f} seconds)")
                
                # Combine destination information
                dest_text = f"{dest.name} {dest.description or ''}"
                
                # Add city and country information (repeated for increased weight)
                if dest.city:
                    # Repeat city information 3 times to increase weight
                    dest_text += f" {dest.city} {dest.city} {dest.city}"
                if dest.country:
                    # Repeat country information 3 times to increase weight
                    dest_text += f" {dest.country} {dest.country} {dest.country}"
                
                # Add subcategory and subtype (simplified)
                if dest.subcategories:
                    if isinstance(dest.subcategories, list):
                        dest_text += " " + " ".join(dest.subcategories[:5])  # Use only first 5
                    elif isinstance(dest.subcategories, str):
                        dest_text += " " + dest.subcategories
                
                if dest.subtypes:
                    if isinstance(dest.subtypes, list):
                        dest_text += " " + " ".join(dest.subtypes[:5])  # Use only first 5
                    elif isinstance(dest.subtypes, str):
                        dest_text += " " + dest.subtypes
                
                # Calculate similarity
                similarity = self.calculate_similarity(query, dest_text)
                
                # Apply additional weight for short queries (less than 3 words)
                if len(query.split()) < 3:
                    # Increase weight if query words are directly in the destination name
                    if any(word in dest.name.lower() for word in query_words):
                        similarity *= 1.5  # 50% increased weight
                    
                    # Greatly increase weight if query words are in city name
                    if dest.city and any(word in dest.city.lower() for word in query_words):
                        similarity *= 2.0  # 100% increased weight
                    
                    # Greatly increase weight if query words are in country name
                    if dest.country and any(word in dest.country.lower() for word in query_words):
                        similarity *= 2.0  # 100% increased weight
                    
                    # Slightly increase weight if query words are in description
                    elif any(word in dest_text.lower() for word in query_words):
                        similarity *= 1.3  # 30% increased weight
                
                # Apply weight if query keywords are directly in the title
                if any(word in dest.name.lower() for word in query_words):
                    similarity *= 1.5  # 50% increased weight
                
                results.append((dest, similarity))
            
            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)
            
            # End measuring processing time
            process_end_time = time.time()
            process_duration = process_end_time - process_start_time
            
            print(f"Search complete: returning top {top_n} of {len(results)} results")
            print(f"Processing time: total {time.time() - start_time:.2f} seconds (data processing: {process_duration:.2f} seconds)")
            
            # Log top 5 results (simplified)
            top_results = [dest.name for dest, _ in results[:5]]
            print(f"Top search results: {', '.join(top_results)}")
            
            # For short queries, return only results with similarity score >= 0.03 (lowered threshold: 0.05 -> 0.03)
            if len(query.split()) < 3:
                filtered_results = [(dest, sim) for dest, sim in results if sim >= 0.03]
                # Use original results if there aren't enough
                if len(filtered_results) < top_n:
                    print(f"Not enough results after similarity filtering ({len(filtered_results)}), using original results")
                    final_results = results[:top_n]
                else:
                    print(f"Filtered to {len(filtered_results)} results by similarity threshold")
                    final_results = filtered_results[:top_n]
            else:
                final_results = results[:top_n]
            
            # Cache results
            search_cache.put(cache_key, final_results)
            
            return final_results
        except Exception as e:
            print(f"Error during destination search: {str(e)}")
            # Fall back to keyword search on error
            print("Falling back to keyword search due to error in semantic search")
            return self.keyword_search(query, destinations, top_n)
    
    def keyword_search(self, query, destinations, top_n=10):
        """
        Simple keyword-based search fallback method.
        Used when advanced search fails or is unavailable.
        
        Parameters:
            query: Search query text
            destinations: List of destinations (Location objects)
            top_n: Number of results to return
            
        Returns:
            List of tuples: [(destination, similarity_score), ...] sorted by similarity score
        """
        try:
            start_time = time.time()
            print("Using basic keyword-based search")
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            # Process all destinations (no limit)
            total_destinations = len(destinations)
            print(f"Keyword search: processing all {total_destinations} destinations")
            
            # Similar words dictionary (for search expansion)
            similar_words = {
                'clean': ['neat', 'tidy', 'spotless', 'immaculate', 'pristine'],
                'cozy': ['comfortable', 'warm', 'snug', 'homely', 'intimate', 'pleasant'],
                'excited': ['thrilling', 'exciting', 'fun', 'entertainment', 'thrill', 'adventure', 'joy', 'happy'],
                'beautiful': ['pretty', 'scenic', 'gorgeous', 'lovely', 'stunning', 'attractive'],
                'quiet': ['peaceful', 'calm', 'serene', 'tranquil', 'silent', 'relaxing'],
                'historic': ['ancient', 'old', 'traditional', 'heritage', 'historical', 'classic'],
                'modern': ['contemporary', 'new', 'trendy', 'stylish', 'innovative'],
                'nature': ['natural', 'outdoor', 'green', 'park', 'garden', 'forest', 'mountain', 'lake', 'river'],
                'food': ['restaurant', 'cuisine', 'dining', 'eat', 'culinary', 'gastronomy', 'delicious'],
                'shopping': ['shop', 'store', 'mall', 'market', 'boutique', 'retail'],
                'family': ['kid', 'child', 'children', 'friendly', 'fun'],
                'luxury': ['luxurious', 'upscale', 'premium', 'elegant', 'fancy', 'high-end'],
                'budget': ['cheap', 'affordable', 'inexpensive', 'economical', 'reasonable'],
                'view': ['vista', 'panorama', 'overlook', 'scenery', 'landscape', 'scenic']
            }
            
            # Expand search terms (include similar words)
            expanded_query_words = set(query_words)
            for word in query_words:
                if word in similar_words:
                    expanded_query_words.update(similar_words[word])
            
            print(f"Search term expansion: {query_words} → {expanded_query_words}")
            
            # Start measuring processing time
            process_start_time = time.time()
            
            results = []
            raw_scores = []  # Store raw scores for normalization
            
            for i, dest in enumerate(destinations):
                # Log progress (every 1000 items)
                if i > 0 and i % 1000 == 0:
                    elapsed = time.time() - process_start_time
                    print(f"Progress: {i}/{len(destinations)} processed ({elapsed:.2f} seconds)")
                
                # Combine destination information
                dest_text = f"{dest.name} {dest.description or ''}".lower()
                
                # Add category information
                if dest.category:
                    dest_text += f" {dest.category}".lower()
                
                # Add city and country information (repeated for increased weight)
                city_match = False
                country_match = False
                
                if dest.city:
                    city_lower = dest.city.lower()
                    # Repeat city information 3 times to increase weight
                    dest_text += f" {city_lower} {city_lower} {city_lower}"
                    # Check for city match
                    city_match = any(word in city_lower for word in query_words)
                
                if dest.country:
                    country_lower = dest.country.lower()
                    # Repeat country information 3 times to increase weight
                    dest_text += f" {country_lower} {country_lower} {country_lower}"
                    # Check for country match
                    country_match = any(word in country_lower for word in query_words)
                
                # Add subcategory information
                if dest.subcategories:
                    if isinstance(dest.subcategories, list):
                        dest_text += " " + " ".join([s.lower() for s in dest.subcategories])
                    elif isinstance(dest.subcategories, str):
                        dest_text += " " + dest.subcategories.lower()
                
                # 1. Exact word matching (high score)
                exact_match_count = sum(1 for word in query_words if f" {word} " in f" {dest_text} ")
                
                # 2. Partial substring matching (medium score)
                partial_match_count = sum(1 for word in query_words if word in dest_text)
                
                # 3. Expanded word matching (low score)
                expanded_match_count = sum(1 for word in expanded_query_words if word in dest_text)
                
                # Calculate combined score (with weights)
                score = 0
                if exact_match_count > 0:
                    score += exact_match_count * 0.6  # Highest weight for exact matching
                if partial_match_count > 0:
                    score += partial_match_count * 0.3  # Medium weight for partial matching
                if expanded_match_count > 0:
                    score += expanded_match_count * 0.1  # Lowest weight for expanded word matching
                
                # Add weight if keywords are in title
                if any(word in dest.name.lower() for word in query_words):
                    score *= 1.5  # 50% increased weight
                
                # Add significant weight if keywords are in city name
                if city_match:
                    score *= 2.0  # 100% increased weight
                
                # Add significant weight if keywords are in country name
                if country_match:
                    score *= 2.0  # 100% increased weight
                
                # Add only results with a score
                if score > 0:
                    raw_scores.append((dest, score))
            
            # Normalize scores and improve distribution
            if raw_scores:
                # Find max score
                max_score = max(score for _, score in raw_scores)
                
                # Normalize scores and improve distribution (log scale)
                for dest, score in raw_scores:
                    # Apply log scale (improve score distribution)
                    normalized_score = 0.2 + (0.8 * (score / max_score))
                    
                    # Apply sigmoid function to smooth score distribution
                    # Center around 0.5 (range 0.2 - 1.0)
                    adjusted_score = 0.2 + (0.8 / (1 + 2.5 * (1 - normalized_score)))
                    
                    results.append((dest, adjusted_score))
            
            # Sort by score
            results.sort(key=lambda x: x[1], reverse=True)
            
            # End measuring processing time
            process_end_time = time.time()
            process_duration = process_end_time - process_start_time
            
            print(f"Keyword search complete: found {len(results)} results")
            print(f"Processing time: total {time.time() - start_time:.2f} seconds (data processing: {process_duration:.2f} seconds)")
            
            return results[:top_n]
        except Exception as e:
            print(f"Error during keyword search: {str(e)}")
            # Last resort fallback: return random results
            import random
            random_results = [(dest, 0.1) for dest in random.sample(list(destinations), min(top_n, len(destinations)))]
            return random_results

# Create singleton instance
nlp_processor = NLPProcessor() 