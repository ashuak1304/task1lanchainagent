import re
import nltk
import string
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NLPUtils:
    """Utility class for natural language processing tasks"""
    
    def __init__(self):
        """Initialize NLP utilities"""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP tasks
        
        Args:
            text: Input text string
            
        Returns:
            list: Preprocessed tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 1
        ]
        
        return processed_tokens
    
    def extract_keywords(self, text, num_keywords=5):
        """
        Extract key terms from text
        
        Args:
            text: Input text string
            num_keywords: Number of keywords to extract
            
        Returns:
            list: Top keywords with their frequencies
        """
        tokens = self.preprocess_text(text)
        
        # Count token frequencies
        word_freq = Counter(tokens)
        
        # Return most common tokens
        return word_freq.most_common(num_keywords)
    
    def extract_sentences(self, text):
        """
        Split text into sentences
        
        Args:
            text: Input text string
            
        Returns:
            list: List of sentences
        """
        if not text:
            return []
        
        return sent_tokenize(text)
    
    def detect_language(self, text):
        """
        Detect the language of the text (simplified version)
        
        Args:
            text: Input text string
            
        Returns:
            str: Detected language code
        """
        # This is a simplified implementation
        # For production, consider using a library like langdetect
        
        # Common words in different languages
        language_markers = {
            'en': ['the', 'and', 'to', 'of', 'a', 'in', 'is', 'that', 'for', 'it'],
            'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se'],
            'fr': ['le', 'la', 'de', 'et', 'à', 'en', 'un', 'être', 'que', 'pour'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
        }
        
        if not text or len(text) < 10:
            return 'en'  # Default to English for short texts
        
        # Lowercase and tokenize
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        # Count occurrences of marker words
        scores = {}
        for lang, markers in language_markers.items():
            scores[lang] = sum(1 for word in words if word in markers)
        
        # Return language with highest score
        if max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return 'en'  # Default to English
    
    def extract_entities(self, text):
        """
        Extract named entities from text (simplified version)
        
        Args:
            text: Input text string
            
        Returns:
            dict: Dictionary of entity types and values
        """
        # This is a simplified implementation
        # For production, consider using spaCy or a dedicated NER model
        
        entities = {
            'emails': self._extract_emails(text),
            'urls': self._extract_urls(text),
            'dates': self._extract_dates(text),
            'phone_numbers': self._extract_phone_numbers(text)
        }
        
        return entities
    
    def _extract_emails(self, text):
        """Extract email addresses from text"""
        if not text:
            return []
        
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.findall(email_pattern, text)
    
    def _extract_urls(self, text):
        """Extract URLs from text"""
        if not text:
            return []
        
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(url_pattern, text)
    
    def _extract_dates(self, text):
        """Extract date patterns from text"""
        if not text:
            return []
        
        # Various date formats
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
            r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4}'  # DD Mon YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return dates
    
    def _extract_phone_numbers(self, text):
        """Extract phone numbers from text"""
        if not text:
            return []
        
        # Various phone number formats
        phone_patterns = [
            r'\+\d{1,3}\s?\(\d{1,4}\)\s?\d{1,4}[-\s]?\d{1,4}',  # +XX (XXXX) XXXX-XXXX
            r'\(\d{3}\)\s?\d{3}[-\s]?\d{4}',                    # (XXX) XXX-XXXX
            r'\d{3}[-\s]?\d{3}[-\s]?\d{4}'                      # XXX-XXX-XXXX
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    def calculate_text_similarity(self, text1, text2):
        """
        Calculate similarity between two texts (using Jaccard similarity)
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Preprocess texts
        tokens1 = set(self.preprocess_text(text1))
        tokens2 = set(self.preprocess_text(text2))
        
        # Calculate Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
