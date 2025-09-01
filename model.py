from transformers import pipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize the sentiment analysis model from Hugging Face
  
        """
        try:
            logger.info("Loading Hugging Face sentiment analysis model...")
            
            # Initialize the sentiment analysis pipeline
            self.classifier = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            logger.info("Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise e
    
    def analyze_sentiment(self, text: str):
        """
        Analyze sentiment of input text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment results with confidence scores
        """
        try:
            # Get prediction from the model
            results = self.classifier(text)
            
            # Extract the results (returns list of all scores)
            sentiment_scores = results[0]  # First (and only) text result
            
            # Find the highest confidence prediction
            best_prediction = max(sentiment_scores, key=lambda x: x['score'])
            
            # Format the response
            return {
                "text": text,
                "sentiment": best_prediction['label'],
                "confidence": round(best_prediction['score'], 4),
                "all_scores": {
                    score['label']: round(score['score'], 4) 
                    for score in sentiment_scores
                }
            }
            
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            return {
                "text": text,
                "sentiment": "error",
                "confidence": 0.0,
                "error": str(e)
            }

# Create a global instance (singleton pattern)
# Why: We want to load the model only once when the app starts
sentiment_analyzer = None

def get_sentiment_analyzer():
    """
    Get the sentiment analyzer instance
    Returns:
        SentimentAnalyzer: The sentiment analyzer instance
    """
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer