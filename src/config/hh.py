from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class HHSettings(BaseModel):
    access_token: str = Field(..., env="HH__ACCESS_TOKEN")
    refresh_token: str = Field(..., env="HH__REFRESH_TOKEN")
    expired_at: datetime = Field(..., env="HH__EXPIRED_AT")
    resume_id: str = Field(..., env="HH__RESUME_ID")

    @field_validator("expired_at", mode="before")
    def parse_custom_datetime(cls, v: str) -> datetime:
        return datetime.strptime(v, "%d.%m.%Y %H:%M:%S")
