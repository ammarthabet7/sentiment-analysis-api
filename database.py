print("🔥 LOADING SENTIMENT-ANALYSIS-API DATABASE.PY!")
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
import sqlalchemy
from datetime import datetime

def get_database_config():
    """
    Smart database configuration - detects environment automatically
    """
    # Check if we're in production (DATABASE_URL environment variable exists)
    production_db_url = os.getenv("DATABASE_URL")
    
    if production_db_url:
        # Production: Use PostgreSQL from environment variable
        print("🐘 Production mode: Connecting to PostgreSQL database...")
        return production_db_url, create_engine(production_db_url)
    else:
        # Development: Use SQLite
        print("🛠️ Development mode: Using SQLite database...")
        sqlite_url = "sqlite:///./sentiment_analysis.db"
        # Correct way to pass SQLite-specific arguments in newer SQLAlchemy
        sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        return sqlite_url, sqlite_engine

# Get database configuration
DATABASE_URL, engine = get_database_config()

# Create database connection for async operations
database = databases.Database(DATABASE_URL)

# Base class for all models
Base = declarative_base()

# Database model for sentiment analysis results
class SentimentResult(Base):
    __tablename__ = "sentiment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    processing_time = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)

# Create tables
def create_tables():
    """Create database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified!")

# Database session management  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """Get database session for synchronous operations"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database operations
async def save_sentiment_result(text: str, sentiment: str, confidence: float, 
                              processing_time: float, user_id: str = None, 
                              ip_address: str = None):
    """Save sentiment analysis result to database"""
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
    """Get analytics about sentiment analysis results"""
    sentiment_counts_query = '''
        SELECT sentiment, COUNT(*) as count, AVG(confidence) as avg_confidence
        FROM sentiment_results 
        GROUP BY sentiment
    '''
    
    overall_stats_query = '''
        SELECT 
            COUNT(*) as total_analyses,
            AVG(processing_time) as avg_processing_time,
            AVG(confidence) as avg_confidence,
            MAX(timestamp) as last_analysis
        FROM sentiment_results
    '''
    
    sentiment_counts = await database.fetch_all(sentiment_counts_query)
    overall_stats = await database.fetch_one(overall_stats_query)
    
    return {
        "sentiment_distribution": [dict(row) for row in sentiment_counts],
        "overall_statistics": dict(overall_stats) if overall_stats else {}
    }

async def get_recent_analyses(limit: int = 10):
    """Get recent sentiment analyses"""
    query = f'''
        SELECT text, sentiment, confidence, processing_time, timestamp
        FROM sentiment_results 
        ORDER BY timestamp DESC 
        LIMIT {limit}
    '''
    
    results = await database.fetch_all(query)
    return [dict(row) for row in results]