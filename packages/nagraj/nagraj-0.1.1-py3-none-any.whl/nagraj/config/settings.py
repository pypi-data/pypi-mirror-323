from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseClassConfig(BaseModel):
    """Configuration for base classes used in the project."""

    entity_base: str = "pydantic.BaseModel"
    aggregate_root_base: str = "pydantic.BaseModel"
    value_object_base: str = "pydantic.BaseModel"
    orm_base: str = "sqlmodel.SQLModel"


class ProjectConfig(BaseModel):
    """Configuration for project generation."""

    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    python_version: str = "^3.12"
    dependencies: Dict[str, str] = Field(
        default_factory=lambda: {
            "fastapi": "^0.115.6",
            "sqlmodel": "^0.0.22",
            "pydantic": "^2.10.5",
            "pydantic-settings": "^2.7.1",
            "alembic": "^1.14.1",
            "argon2-cffi": "^23.1.0",
            "uvicorn": "^0.34.0",
            "python-multipart": "^0.0.20",
            "python-jose": "^3.3.0",
        }
    )
    dev_dependencies: Dict[str, str] = Field(
        default_factory=lambda: {
            "pytest": "^8.3.4",
            "pytest-cov": "^6.0.0",
            "pytest-asyncio": "^0.25.2",
            "ruff": "^0.9.2",
        }
    )


class Settings(BaseSettings):
    """Global settings for Nagraj."""

    model_config = SettingsConfigDict(
        env_prefix="NAGRAJ_",
        env_nested_delimiter="__",
    )

    config_path: Path = Field(
        default=Path.home() / ".config" / "nagraj" / "config.yaml"
    )
    template_path: Path = Field(default=Path(__file__).parent.parent / "templates")
    base_classes: BaseClassConfig = Field(default_factory=BaseClassConfig)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file and environment variables."""
        settings = cls()

        # Create config directory if it doesn't exist
        settings.config_path.parent.mkdir(parents=True, exist_ok=True)

        if settings.config_path.exists():
            try:
                with settings.config_path.open("r") as f:
                    yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # Update settings from YAML
                    if "base_classes" in yaml_config:
                        settings.base_classes = BaseClassConfig(
                            **yaml_config["base_classes"]
                        )
                    # Add more configuration sections as needed
            except Exception as e:
                print(
                    f"Warning: Failed to load config from {settings.config_path}: {e}"
                )

        # Ensure template path exists
        if not settings.template_path.exists():
            raise ValueError(f"Template path does not exist: {settings.template_path}")

        return settings


# Global settings instance
settings = Settings.load()
