import os
import json
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
# Default DATA_DIR looks for DATA directory adjacent to backend or inside workspace
DEFAULT_DATA_DIR = BASE_DIR.parent / "DATA"


class Settings(BaseSettings):
    """System configuration for RUDRA Smart Campus Backend."""
    
    PROJECT_NAME: str = "RUDRA Smart Campus AI System"
    VERSION: str = "1.0.0"
    
    # Data Directory Path
    DATA_DIR: Path = DEFAULT_DATA_DIR
    
    # LLM Settings
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"

    # Authentication Settings
    # AUTH_DEV_MODE=true (default) accepts legacy demo tokens ("Bearer user_<id>") for local development.
    # AUTH_DEV_MODE=false verifies every request as a real Firebase ID token (JWT) and rejects everything else.
    AUTH_DEV_MODE: bool = True
    # Firebase project id used to verify ID token signature/audience/issuer.
    FIREBASE_PROJECT_ID: str = "rudra-ff130"
    
    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins safely."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            try:
                parsed = json.loads(self.CORS_ORIGINS)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return ["*"]

    def resolved_data_dir(self) -> Path:
        """Resolves data directory to an existing absolute Path."""
        path = Path(self.DATA_DIR)
        if not path.is_absolute():
            path = (BASE_DIR / path).resolve()
        
        # Fallback check if DATA is in current working directory or parent
        if not path.exists():
            parent_data = (BASE_DIR.parent / "DATA").resolve()
            if parent_data.exists():
                return parent_data
        return path


settings = Settings()
