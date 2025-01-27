"""Settings."""

from datetime import date

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings from .env file.

    Args:
        BaseSettings (pydantic.BaseSettings): Base settings to override

    Raises
        ValueError: if something is wrong with .env file
    """

    model_config = ConfigDict(extra="allow")

    COST_INFRA_PRICING_RATE: float = 0.14  # the machine pricing rate in $/min

    COST_DEV_HOURLY_RATE: float = 0.6 * 60  # salary in $/60 min

    RECENCY_REFERENCE_DATE: date = date.today()

    RECENCY_N_LAST: int = 3


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
