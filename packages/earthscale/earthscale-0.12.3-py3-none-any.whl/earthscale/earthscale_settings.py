from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EarthscaleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EARTHSCALE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = "https://mvkmibwhbplfmurjawlk.supabase.co"
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12a21pYndoYnBsZm11cmphd2xrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTg4MTcyMjEsImV4cCI6MjAzNDM5MzIyMX0.7Vp3C__qs9Cdb0HD1Zx0uqD5DOem70_k6NDkzbMutyQ"  # noqa: E501
    credentials_file: Path = Path().home() / ".earthscale" / "credentials.json"
    user_email: str | None = None
    user_password: str | None = None
