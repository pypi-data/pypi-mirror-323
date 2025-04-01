# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum


class ModelLocationType(str, Enum):
  LOCAL = "local"
  API = "api"


class ModelParam(BaseModel):
  key: str | None = None
  value: Any | None = None


class ModelConfig(BaseModel):
  key: str
  location: ModelLocationType
  tokenizer: str
  context_size: int = 0
  name: Optional[str] = None
  model: Optional[str] = None
  path: Optional[str] = None
  repo_id: Optional[str] = None
  filename: Optional[str] = None
  params: Optional[list[ModelParam]] = None
  publisher: Optional[str] = None
