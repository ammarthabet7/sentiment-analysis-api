from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
import sqlalchemy
from datetime import datetime

# Database configuration
DATABASE_URL = "sqlite:///./sentiment_analysis.db"

# Create database connection
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base class for all models
Base = declarative_base()

# Database model for sentiment analysis results
class SentimentResult(Base):
    """
    Database model to store sentiment analysis results
    
    """
    __tablename__ = "sentiment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)  # Original text analyzed
    sentiment = Column(String(50), nullable=False)  # POSITIVE/NEGATIVE/NEUTRAL
    confidence = Column(Float, nullable=False)  # Model confidence score
    processing_time = Column(Float, nullable=False)  # How long analysis took
    timestamp = Column(DateTime, default=datetime.utcnow)  # When analysis happened
    
    # Optional: Add user tracking
    user_id = Column(String(100), nullable=True)  # For user analytics
    ip_address = Column(String(45), nullable=True)  # For geographic analytics

# Create tables
def create_tables():
    """
    Create database tables if they don't exist
    """
    Base.metadata.create_all(bind=engine)

# Database session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """
    Get database session for synchronous operations

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database operations
async def save_sentiment_result(text: str, sentiment: str, confidence: float, 
                              processing_time: float, user_id: str = None, 
                              ip_address: str = None):
    """
    Save sentiment analysis result to database
    
    Args:
        text: Original text that was analyzed
        sentiment: Detected sentiment (POSITIVE/NEGATIVE/NEUTRAL)
        confidence: Model confidence score
        processing_time: Time taken for analysis
        user_id: Optional user identifier
        ip_address: Optional IP for analytics
    
    Returns:
        int: ID of saved record
    """
    query = sqlalchemy.insert(SentimentResult).values(
        text=text,
        sentiment=sentiment,
        confidence=confidence,
        processing_time=processing_time,
        user_id=user_id,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
    
    result = await database.execute(query)
    return result

async def get_sentiment_analytics():
    """
    Get analytics about sentiment analysis results
    
    Returns:
        dict: Analytics data including counts and averages
    """
    # Count by sentiment type
    sentiment_counts_query = """
        SELECT sentiment, COUNT(*) as count, AVG(confidence) as avg_confidence
        FROM sentiment_results 
        GROUP BY sentiment
    """
    
    # Overall statistics
    overall_stats_query = """
        SELECT 
            COUNT(*) as total_analyses,
            AVG(processing_time) as avg_processing_time,
            AVG(confidence) as avg_confidence,
            MAX(timestamp) as last_analysis
        FROM sentiment_results
    """
    
    sentiment_counts = await database.fetch_all(sentiment_counts_query)
    overall_stats = await database.fetch_one(overall_stats_query)
    
    return {
        "sentiment_distribution": [dict(row) for row in sentiment_counts],
        "overall_statistics": dict(overall_stats) if overall_stats else {}
    }

async def get_recent_analyses(limit: int = 10):
    """
    Get recent sentiment analyses
    
    Args:
        limit: Number of recent results to return
        
    Returns:
        list: Recent sentiment analysis results
    """
    query = f"""
        SELECT text, sentiment, confidence, processing_time, timestamp
        FROM sentiment_results 
        ORDER BY timestamp DESC 
        LIMIT {limit}
    """
    
    results = await database.fetch_all(query)
    return [dict(row) for row in results]