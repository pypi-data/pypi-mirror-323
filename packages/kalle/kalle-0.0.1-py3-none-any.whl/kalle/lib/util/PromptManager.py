# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from typing import Optional
from jinja2 import Template

from kalle.domain.PromptTemplate import PromptTemplate


class PromptManager:

  def __init__(
      self,
      config,
      /,
      system_prompt_template: Optional[PromptTemplate] = None,
      system_prompt: Optional[str] = None,
      prompt_template: Optional[PromptTemplate] = None,
      piped_content: Optional[str] = None,
      param_content: Optional[str] = None,
  ):
    self.config = config
    self.system_prompt_template = system_prompt_template
    self.system_prompt = system_prompt
    self.prompt_template = prompt_template
    self.piped_content = piped_content
    self.param_content = param_content

  def compile_prompt(self, prompt=None):
    final_prompt = prompt or self.param_content or ""
    if self.piped_content is not None:
      final_prompt = "\n\n---\n".join([final_prompt, self.piped_content])

    if self.prompt_template is not None and self.prompt_template.value is not None and self.prompt_template.value != "":
      template = Template(self.prompt_template.value)
      final_prompt = template.render(
          {
              "content": final_prompt,
          }
      )

    return final_prompt

  def compile_system_prompt(self, prompt=None):
    final_prompt = self.config.prompts["kalle_system_prompt"].value
    if prompt is not None:
      final_prompt = prompt
    elif self.system_prompt is not None:
      final_prompt = self.system_prompt

    if self.system_prompt_template is not None and self.system_prompt_template.value is not None:
      template = Template(self.system_prompt_template.value)
      final_prompt = template.render(
          {
              "system_prompt": final_prompt,
          }
      )

    return final_prompt

  def compile_tool_prompt(self, tools, prompt=None):
    final_prompt = self.config.prompts["base_tool_prompt"].value or ""

    if prompt is not None:
      final_prompt = prompt

    for name, tool in tools.items():
      final_prompt += "\n\n" + tool.get_prompt()

    return final_prompt
