from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    people: int = Field(default=1, ge=1, description="Number of travelers")
    budget_total: Optional[float] = Field(default=None, ge=0, description="Total budget in USD")
    interests: List[str] = Field(default_factory=list, description="e.g., ['museums','food']")

class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: str  # ISO date (YYYY-MM-DD)
    days: int = Field(default=3, ge=1, le=30)
    profile: UserProfile = Field(default_factory=UserProfile)

class DayPlan(BaseModel):
    day: int
    date: str
    activities: List[str]
    notes: Optional[str] = None

class Plan(BaseModel):
    destination: str
    total_estimated_cost: float
    currency: str = "USD"
    days: List[DayPlan]
    trace: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
