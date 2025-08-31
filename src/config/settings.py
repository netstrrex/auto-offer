from pathlib import Path

from pydantic_settings import BaseSettings

from config.hh import HHSettings
from config.job import JobSettings

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    hh: HHSettings
    job: JobSettings

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False
        env_nested_delimiter = "__"


settings = Settings()
