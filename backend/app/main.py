import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router


app = FastAPI(
    title="SQL Detective API",
    version="0.1.0",
    description="Backend API for the SQL game project.",
)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# Optional override from deployment env, comma-separated.
# Example: CORS_ORIGINS="https://a.vercel.app,https://b.vercel.app"
extra_origins = os.getenv("CORS_ORIGINS", "").strip()
if extra_origins:
    origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Allow local dev servers on any localhost/127.0.0.1 port (Vite may switch ports).
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "SQL Detective API is running"}
