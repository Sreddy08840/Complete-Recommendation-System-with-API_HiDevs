
from fastapi import FastAPI
from .config import settings
from .routers import (
    users,
    content,
    skills,
    interactions,
    recommendations,
)

app = FastAPI(title="Recommendation System API")

# Include all routers
app.include_router(users.router)
app.include_router(content.router)
app.include_router(skills.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

