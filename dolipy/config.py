from typing import Optional

from pydantic import BaseSettings, Field


class DoliConfig(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")
    api_key: Optional[str] = Field(None, env="API_KEY",)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
