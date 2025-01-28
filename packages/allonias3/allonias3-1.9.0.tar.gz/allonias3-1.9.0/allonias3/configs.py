from __future__ import annotations

from alloniaconfigs import Configs as BaseConfigs
from pydantic import UUID4, BaseModel, Field, HttpUrl


class ConfigSchema(BaseModel):
    USER_TOKEN_ID: str = Field(min_length=16, max_length=16)
    USER_TOKEN_SECRET: str = Field(min_length=32, max_length=32)
    TRACK_ID: UUID4
    PROJECT_ID: UUID4
    USER_ID: UUID4
    BUCKET_NAME: str = Field(min_length=1)
    S3_PROXY_URL: HttpUrl
    USE_BOTO: bool = Field(False)
    REGION_NAME: str = Field("XXXX", min_length=1)


class Configs(BaseConfigs):
    schema = ConfigSchema

    @property
    def s3_proxy_url(self) -> str:
        return str(self.S3_PROXY_URL)

    @property
    def persistent_bucket_name(self) -> str:
        """From :obj:`~Envs.BUCKET_NAME`, will construct the persistent bucket
        name (if different) and return it. Returns None if neither the bucket
        name nor the track ID were defined in the env vars."""
        return (
            self.BUCKET_NAME.replace("non-persistent", "persistent")
            if self.BUCKET_NAME is not None
            and self.BUCKET_NAME.endswith("non-persistent")
            else self.BUCKET_NAME
        )

    @property
    def non_persistent_bucket_name(self) -> str:
        """From :obj:`~Envs.BUCKET_NAME`, will construct the non-persistent
        bucket name (if different) and return it. Returns None if neither the
        bucket name nor the track ID were defined in the env vars."""
        return (
            self.BUCKET_NAME.replace("persistent", "non-persistent")
            if self.BUCKET_NAME is not None
            and not self.BUCKET_NAME.endswith("non-persistent")
            else self.BUCKET_NAME
        )
