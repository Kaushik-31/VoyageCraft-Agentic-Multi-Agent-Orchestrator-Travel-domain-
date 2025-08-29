from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VoyageCraft Backend", version="0.1.0")

# CORS: allow the frontend (we'll set exact origin later in env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
