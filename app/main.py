from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.api.admin.problems import router as admin_problems_router

app = FastAPI()

@app.get("/db-check")
def db_check():
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1")) 
        db.close()
        return {"db_status": "connected"}
    except Exception as e:
        return {"db_status": "error", "details": str(e)}


# Include admin problems router
app.include_router(admin_problems_router, prefix="/problems")