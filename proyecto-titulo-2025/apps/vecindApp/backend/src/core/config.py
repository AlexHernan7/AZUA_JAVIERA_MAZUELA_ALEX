from abc import ABC, abstractmethod
from functools import lru_cache
from os import getenv, path
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentLoader(ABC):
    @abstractmethod
    def load(self):
        pass


class DotEnvLoader(EnvironmentLoader):
    def load(self):
        load_dotenv()


class APISettings(BaseModel):
    """Configuración de API."""

    v1_str: str = "/api"
    project_name: str = "vecindapp"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_days: int = 30


class GoogleOAuthSettings(BaseModel):
    """Configuración OAuth."""

    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "openid email profile"


class NewsAPISettings(BaseModel):
    """Configuración de la API de noticias APITube."""

    api_key: str
    base_url: str = Field(default="https://api.apitube.io/v1")
    timeout: int = Field(default=30)
    max_articles: int = Field(default=100)


class FileSettings(BaseModel):
    """Configuración de archivos."""

    upload_directory: str = Field(default="uploads")
    base_url: str = Field(default="/files")
    max_file_size: int = Field(default=10 * 1024 * 1024)
    allowed_extensions: list[str] = Field(default=[".jpg", ".jpeg", ".png", ".pdf"])


class DatabaseSettings(BaseModel):
    """Configuración de base de datos."""

    user: str
    password: str
    host: str
    port: str
    name: str
    db_schema: str = "vecindapp"
    pool_size: int = 20
    max_overflow: int = 10

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class MigrationSettings(BaseModel):
    """Configuración de migraciones."""

    base_dir: str = Field(default="alembic")
    development_versions_dir: str = Field(default="versions/development")
    production_versions_dir: str = Field(default="versions/production")

    def get_versions_path(self, environment: str, script_location: str) -> str:
        """Obtiene la ruta de versiones según el entorno."""
        if environment.upper() in ["DEVELOPMENT", "STAGING"]:
            return path.join(script_location, self.development_versions_dir)
        return path.join(script_location, self.production_versions_dir)


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    debug: bool = False
    environment: Literal["DEVELOPMENT", "STAGING", "PRODUCTION"]
    database: DatabaseSettings
    migrations: MigrationSettings = MigrationSettings()
    api: APISettings
    google_oauth: GoogleOAuthSettings
    news_api: NewsAPISettings
    files: FileSettings = Field(default_factory=FileSettings)

    @classmethod
    def get_database_settings(cls, environment: str) -> dict[str, Any]:
        """Configuración de BD según el entorno."""
        if environment.upper() == "DEVELOPMENT":
            return {
                "user": "postgres",
                "password": "admin",
                "host": "localhost",
                "port": "5432",
                "name": "postgres",
                "db_schema": "vecindapp",
                "pool_size": 20,
                "max_overflow": 10,
            }
        else:
            return {
                "user": getenv("DB_USER_QP"),
                "password": getenv("DB_PASSWORD_QP"),
                "host": getenv("DB_HOST_QP"),
                "port": getenv("DB_PORT_QP"),
                "name": getenv("DB_DATABASE_QP"),
                "db_schema": getenv("DB_SCHEMA"),
                "pool_size": 20,
                "max_overflow": 10,
            }

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", validate_default=True, extra="ignore"
    )


@lru_cache
def get_settings(env_loader: EnvironmentLoader = DotEnvLoader()) -> Settings:
    """Obtiene configuración cacheada."""
    env_loader.load()
    environment = getenv("ENVIRONMENT")

    return Settings(
        environment=environment,
        debug=getenv("DEBUG", "false").lower() == "true",
        database=DatabaseSettings(**Settings.get_database_settings(environment)),
        api=APISettings(
            secret_key=getenv("SECRET_KEY"),
        ),
        google_oauth=GoogleOAuthSettings(
            client_id=getenv("GOOGLE_OAUTH_CLIENT_ID", "ADMIN"),
            client_secret=getenv("GOOGLE_OAUTH_CLIENT_SECRET", "ADMIN"),
            redirect_uri=getenv("GOOGLE_OAUTH_REDIRECT_URI", "ADMIN"),
        ),
        news_api=NewsAPISettings(
            api_key=getenv("NEWS_API_KEY", "demo_key"),  # Usar una key de demo por defecto
        ),
    )


settings = get_settings()
