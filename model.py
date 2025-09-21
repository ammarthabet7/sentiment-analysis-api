from textblob import TextBlob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize the sentiment analysis using TextBlob
        """
        logger.info("Loading TextBlob sentiment analyzer...")
        logger.info("TextBlob analyzer ready!")

    def analyze_sentiment(self, text: str):
        """
        Analyze sentiment using TextBlob
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Convert polarity to readable sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Convert polarity to confidence (0 to 1)
            confidence = abs(polarity)
            
            return {
                "text": text,
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
                "all_scores": {
                    "positive": max(0, polarity),
                    "negative": max(0, -polarity),
                    "neutral": 1 - abs(polarity)
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

# Global instance
sentiment_analyzer = None

def get_sentiment_analyzer():
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer
