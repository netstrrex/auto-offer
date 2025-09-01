from pydantic import BaseModel, Field


class JobSettings(BaseModel):
    search_query: str = Field(..., env="JOB__SEARCH_QUERY")
    experience: str = Field(..., env="JOB__EXPERIENCE")
