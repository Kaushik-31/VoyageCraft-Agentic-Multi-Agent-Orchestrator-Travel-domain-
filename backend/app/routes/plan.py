from fastapi import APIRouter
from utils.types import TripRequest
from orchestrators.react_loop import ReactLoop

router = APIRouter()

@router.post("/plan")
def generate_plan(request: TripRequest):
    orch = ReactLoop()
    plan = orch.run(request)
    return plan.model_dump()
