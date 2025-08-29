from fastapi import APIRouter
from orchestrators.react_loop import ReactLoop
from utils.types import TripRequest, Plan

router = APIRouter(prefix="/plan", tags=["plan"])

@router.post("", response_model=Plan)
def create_plan(req: TripRequest) -> Plan:
    orch = ReactLoop()
    return orch.run(req)
