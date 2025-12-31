from fastapi import FastAPI
from app.api.routers.router import api_router
# from app.core.config import settings

app = FastAPI(
    title="LeagueScraper",
    version="1.0.0"
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to the API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)