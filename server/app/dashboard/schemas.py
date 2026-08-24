from pydantic import BaseModel


class DashboardRead(BaseModel):
    total_complaints: int
    open: int
    in_progress: int
    resolved: int
    overdue: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
