from pydantic import BaseModel, Field


class AdminSettingsRead(BaseModel):
    overdue_threshold_days: int


class OverdueThresholdUpdate(BaseModel):
    days: int = Field(gt=0)
