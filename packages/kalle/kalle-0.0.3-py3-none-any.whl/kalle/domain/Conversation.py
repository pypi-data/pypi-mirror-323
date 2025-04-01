# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from pydantic import BaseModel
from typing import Optional

from kalle.domain.Profile import Profile


class ConversationMetadata(BaseModel):
  version: float = 0.0
  system_prompt: Optional[str] = None
  profile: Optional[Profile] = None


class ConversationMessage(BaseModel):
  timestamp: Optional[float] = None
  system_prompt: Optional[str] = None
  profile: Optional[Profile] = None
  role: str | None = None
  piped_content: Optional[str] = None
  param_content: Optional[str] = None
  tool_prompt: Optional[str] = None
  tool_response: Optional[str] = None
  content: str | None = None

  def get_message(self):
    return {"role": self.role, "content": self.content}


class Conversation(BaseModel):
  metadata: ConversationMetadata = ConversationMetadata(version=0.2)
  conversation: list[ConversationMessage] = []

  def get_messages(self):
    messages = []
    for c in self.conversation:
      messages.append(c.get_message())

    return messages
