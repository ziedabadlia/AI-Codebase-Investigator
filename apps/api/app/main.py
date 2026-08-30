import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes.repositories import router as repositories_router
from app.api.routes.investigate import router as investigate_router

# Load environment files
load_dotenv()

# Initialize FastAPI App
app = FastAPI(
    title="AI Codebase Investigator API",
    description="Backend API for indexing GitHub repositories and executing LangGraph codebase investigations.",
    version="0.1.0"
)

# CORS Configuration
frontend_url = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:3000")
# Normalize frontend url by converting backend address back to client if needed
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    frontend_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_health():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Register routers
app.include_router(repositories_router)
app.include_router(investigate_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
