from fastapi import FastAPI
from app.api.resume import router as resume_router

app = FastAPI()

app.include_router(resume_router, prefix="/api", tags=["Resume Upload"])
