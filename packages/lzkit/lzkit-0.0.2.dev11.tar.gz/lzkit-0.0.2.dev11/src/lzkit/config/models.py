from pydantic import BaseModel, Field


class Kit(BaseModel):
    """Top-level config model for lzkit."""

    version: int = Field(default=1, description="Kit config version")
