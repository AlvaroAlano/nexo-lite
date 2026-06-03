from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import periods, expenses, templates, summary, categories

app = FastAPI(
    title="Nexo Lite API",
    description="Monthly financial check-in system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(periods.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(categories.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
