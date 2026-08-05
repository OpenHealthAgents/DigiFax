"""
config.py
Pydantic Settings loader managing environment variables for production integrations.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-level configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 1. Identity & Access Management (bezs-iam)
    iam_url: str = "http://localhost:5001"
    iam_jwks_url: str = "http://localhost:5001/api/auth/jwks"

    # 2. Distributed Event Queue (Celery + Redis)
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # 3. Persistent Object Storage (S3 / MinIO / LocalStack)
    aws_s3_bucket_name: str = "medingest-documents"
    aws_s3_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str = "minio_admin"
    aws_secret_access_key: str = "minio_secret"
    aws_region_name: str = "us-east-1"
    aws_s3_force_path_style: bool = True

    # 4. Feature flags / runtime configurations
    use_persistent_storage: bool = False  # Set True to switch from InMemoryStorage to S3Storage


# Singleton instance of settings
settings = Settings()
