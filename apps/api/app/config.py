from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Copilot API"
    app_env: str = "local"
    app_debug: bool = True
    app_version: str = "0.1.0"

    embedding_model: str = "all-MiniLM-L6-v2"

    max_upload_size_mb: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def raw_data_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def metadata_dir(self) -> Path:
        return self.data_dir / "metadata"

    @property
    def metadata_file_path(self) -> Path:
        return self.metadata_dir / "documents.json"

    @property
    def embeddings_file_path(self) -> Path:
        return self.processed_data_dir / "embeddings.json"


settings = Settings()
settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
settings.metadata_dir.mkdir(parents=True, exist_ok=True)