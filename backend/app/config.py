from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env", encoding="utf-8-sig")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8-sig", extra="ignore")

    app_name: str = "Web Training Platform"
    app_env: str = Field(default="development", alias="APP_ENV")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-v4-flash", alias="DEEPSEEK_MODEL")
    deepseek_live: bool = Field(default=False, alias="DEEPSEEK_LIVE")
    deepseek_timeout_seconds: float = Field(default=3, alias="DEEPSEEK_TIMEOUT_SECONDS")
    data_dir: Path = ROOT_DIR / "backend" / ".data"
    upload_dir: Path = ROOT_DIR / "backend" / "uploads"
    chroma_dir: Path = ROOT_DIR / "backend" / ".chroma"
    rag_backend: str = Field(default="hybrid", alias="RAG_BACKEND")
    rag_collection: str = Field(default="springboot_course", alias="RAG_COLLECTION")
    rag_chunk_size: int = Field(default=900, alias="RAG_CHUNK_SIZE")
    rag_top_k: int = Field(default=4, alias="RAG_TOP_K")
    rag_snippet_size: int = Field(default=180, alias="RAG_SNIPPET_SIZE")
    rag_lesson_boost: float = Field(default=0.35, alias="RAG_LESSON_BOOST")
    rag_concept_boost: float = Field(default=0.25, alias="RAG_CONCEPT_BOOST")
    rag_vector_candidates: int = Field(default=10, alias="RAG_VECTOR_CANDIDATES")
    upload_max_bytes: int = Field(default=2 * 1024 * 1024, alias="UPLOAD_MAX_BYTES")
    web_search_enabled: bool = Field(default=False, alias="WEB_SEARCH_ENABLED")
    web_search_provider: str = Field(default="tavily", alias="WEB_SEARCH_PROVIDER")
    web_search_api_key: str = Field(default="", alias="WEB_SEARCH_API_KEY")
    web_search_top_k: int = Field(default=3, alias="WEB_SEARCH_TOP_K")
    web_search_timeout_seconds: float = Field(default=8, alias="WEB_SEARCH_TIMEOUT_SECONDS")

    @property
    def db_path(self) -> Path:
        return self.data_dir / "learning.sqlite"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return settings
