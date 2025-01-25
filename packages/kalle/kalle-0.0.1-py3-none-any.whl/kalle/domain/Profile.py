# kalle
# Copyright (C) 2024 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional

from kalle.domain.Connector import Connector
from kalle.domain.ModelConfig import ModelParam


class Profile(BaseModel):
  connector: Connector
  key: Optional[str] = None
  name: Optional[str] = None
  model: Optional[str] = None
  model_params: Optional[list[ModelParam]] = None
