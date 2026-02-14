from fastapi import FastAPI
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.monitor_service import MonitorService
from app.services.posting_engine import PostingEngineService
from app.crud.user import user as crud_user
from app.api.v1.api import api_router # Added this import back
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="X Growth Automation API")

# Re-added the router inclusion, assuming it's still needed
app.include_router(api_router, prefix=settings.API_V1_STR)

async def run_monitoring_loop():
    logger.info("Starting Monitoring Loop...")
    while True:
        try:
            db = SessionLocal()
            # For MVP, just picking the first user or a specific one.
            # In established app, we'd iterate over active users.
            users = db.query(crud_user.model).filter(crud_user.model.is_active == True).all()
            
            for user in users:
                monitor = MonitorService(db, user)
                # Monitor home timeline
                await monitor.monitor_home_timeline()
                # Monitor keywords
                await monitor.monitor_keywords()
                
            db.close()
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        
        await asyncio.sleep(60 * 5) # Run every 5 minutes

async def run_posting_loop():
    logger.info("Starting Posting Loop...")
    while True:
        try:
            db = SessionLocal()
            users = db.query(crud_user.model).filter(crud_user.model.is_active == True).all()
            
            for user in users:
                engine = PostingEngineService(db, user)
                await engine.process_queue()
                
            db.close()
        except Exception as e:
            logger.error(f"Error in posting loop: {e}")
            
        await asyncio.sleep(60) # P Check every minute

@app.on_event("startup")
async def startup_event():
    # Fallback: Create tables if not exist (for MVP resilience)
    try:
        from app.core.database import engine, Base
        from app.models import User, Tweet, ReplyCandidate, Keyword, Persona
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created/verified.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")

    # Start background tasks
    try:
        asyncio.create_task(run_monitoring_loop())
        asyncio.create_task(run_posting_loop())
    except Exception as e:
        logger.error(f"Failed to start background tasks: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to X Growth Automation API", "status": "running"}
