from fastapi import FastAPI
from app.api.routers.router import api_router

app = FastAPI(title="LeagueScraper", version="1.0.0")
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
