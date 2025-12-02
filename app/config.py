from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4.1"
    openai_embedding_model: str = "text-embedding-3-large"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "second_brain"
    postgres_user: str = "second_brain"
    postgres_password: str = "second_brain_password"

    vector_dim: int = 3072  # adjust to embedding model

    app_env: str = "development"
    app_debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
