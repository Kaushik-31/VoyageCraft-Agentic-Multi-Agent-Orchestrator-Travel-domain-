from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.plan import router as plan_router

app = FastAPI(title="VoyageCraft Backend", version="0.1.0")

# CORS: allow the frontend (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(plan_router)

@app.get("/health")
def health():
    return {"status": "ok"}
