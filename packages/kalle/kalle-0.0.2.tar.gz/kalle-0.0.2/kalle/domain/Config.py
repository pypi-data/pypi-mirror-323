# kalle
# Copyright (C) 2024 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional, Dict

from kalle.domain.Profile import Profile
from kalle.domain.Pattern import Pattern
from kalle.domain.ModelConfig import ModelConfig
from kalle.domain.PromptTemplate import PromptTemplate


class Config(BaseModel):
  appname: str = "kalle"
  appauthor: str = "fe2"
  conversation_key: Optional[str] = None
  use_memory: bool = False
  debug: bool = False
  profiles: Dict[str, Profile]
  patterns: Dict[str, Pattern]
  models_map: Dict[str, dict[str, ModelConfig]]
  prompt_templates: Dict[str, PromptTemplate]
