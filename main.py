from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import time
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from model import get_sentiment_analyzer
from database import (
    database, create_tables, save_sentiment_result, 
    get_sentiment_analytics, get_recent_analyses
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Sentiment Analysis API with Database",
    description="Production-ready sentiment analysis with data persistence and analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'sentiment_requests_total',
    'Total number of sentiment analysis requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'sentiment_request_duration_seconds',
    'Time spent processing sentiment requests',
    ['method', 'endpoint']
)

# Database metrics
DB_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'status']
)

# Pydantic models
class SentimentRequest(BaseModel):
    text: str
    user_id: str = None  # Optional user tracking
    
    class Config:
        schema_extra = {
            "example": {
                "text": "I love this enhanced API with database support!",
                "user_id": "user_123"
            }
        }

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    all_scores: dict
    processing_time_seconds: float
    analysis_id: int  # New: Database record ID
    timestamp: str

class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoint"""
    sentiment_distribution: list
    overall_statistics: dict
    recent_analyses: list

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """
    Initialize database and connections on startup
    
    Why we do this:
    - Create database tables if they don't exist
    - Establish database connection pool
    - Pre-load AI model
    """
    logger.info("Starting Sentiment Analysis API with Database...")
    
    try:
        # Connect to database
        await database.connect()
        logger.info("Database connected successfully!")
        
        # Create tables
        create_tables()
        logger.info("Database tables verified/created!")
        
        # Pre-load the model
        analyzer = get_sentiment_analyzer()
        logger.info("AI Model pre-loaded successfully!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown():
    """
    Clean up database connections on shutdown
    """
    logger.info("Shutting down...")
    await database.disconnect()
    logger.info("Database disconnected.")

# API Endpoints
@app.get("/")
async def root():
    """Enhanced root endpoint with database info"""
    return {
        "message": "Enhanced Sentiment Analysis API with Database!",
        "version": "2.0.0",
        "features": [
            "Hugging Face sentiment analysis",
            "SQLite database persistence",
            "Analytics and reporting",
            "Prometheus monitoring"
        ],
        "endpoints": {
            "analyze": "/analyze",
            "analytics": "/analytics",
            "recent": "/recent",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check including database"""
    try:
        # Test AI model
        analyzer = get_sentiment_analyzer()
        
        # Test database connection
        await database.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "components": {
                "api": "running",
                "model": "loaded",
                "database": "connected"
            },
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
    http_request: Request,
    analyzer = Depends(get_sentiment_analyzer)
):
    """
    Enhanced sentiment analysis with database storage
    """
    start_time = time.time()
    
    try:
        # Input validation
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 1000:
            raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
        
        # Perform sentiment analysis
        result = analyzer.analyze_sentiment(request.text)
        processing_time = time.time() - start_time
        
        # Get client IP for analytics
        client_ip = http_request.client.host
        
        # Save to database
        try:
            analysis_id = await save_sentiment_result(
                text=result["text"],
                sentiment=result["sentiment"],
                confidence=result["confidence"],
                processing_time=processing_time,
                user_id=request.user_id,
                ip_address=client_ip
            )
            
            DB_OPERATIONS.labels(operation="save", status="success").inc()
            
        except Exception as db_error:
            logger.error(f"Database save failed: {db_error}")
            DB_OPERATIONS.labels(operation="save", status="error").inc()
            # Continue without failing the request
            analysis_id = -1
        
        # Update metrics
        REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="success").inc()
        REQUEST_DURATION.labels(method="POST", endpoint="/analyze").observe(processing_time)
        
        # Return enhanced response
        return SentimentResponse(
            text=result["text"],
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            all_scores=result["all_scores"],
            processing_time_seconds=round(processing_time, 4),
            analysis_id=analysis_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
    except HTTPException:
        REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="client_error").inc()
        raise
    except Exception as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="server_error").inc()
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Get sentiment analysis analytics and statistics
    
    New endpoint that shows:
    - Sentiment distribution (how many positive/negative/neutral)
    - Average confidence scores
    - Processing time statistics
    - Recent analysis activity
    """
    try:
        # Get analytics data
        analytics = await get_sentiment_analytics()
        recent = await get_recent_analyses(limit=5)
        
        DB_OPERATIONS.labels(operation="read", status="success").inc()
        
        return AnalyticsResponse(
            sentiment_distribution=analytics["sentiment_distribution"],
            overall_statistics=analytics["overall_statistics"],
            recent_analyses=recent
        )
        
    except Exception as e:
        DB_OPERATIONS.labels(operation="read", status="error").inc()
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@app.get("/recent")
async def get_recent_analyses_endpoint(limit: int = 10):
    """
    Get recent sentiment analyses
    
    Args:
        limit: Number of recent analyses to return (max 50)
    """
    if limit > 50:
        limit = 50
        
    try:
        recent = await get_recent_analyses(limit=limit)
        DB_OPERATIONS.labels(operation="read", status="success").inc()
        
        return {
            "recent_analyses": recent,
            "count": len(recent),
            "limit": limit
        }
        
    except Exception as e:
        DB_OPERATIONS.labels(operation="read", status="error").inc()
        logger.error(f"Recent analyses error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recent analyses")

@app.get("/metrics")
async def get_metrics():
    """Enhanced metrics endpoint"""
    return PlainTextResponse(
        content=generate_latest(),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)