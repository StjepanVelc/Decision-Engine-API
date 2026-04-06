from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_decisions: int
    approve_count: int
    review_count: int
    reject_count: int
    approve_rate: float
    reject_rate: float
    review_rate: float
    success_rate: float  # alias za approve_rate, jasno za portfolio
