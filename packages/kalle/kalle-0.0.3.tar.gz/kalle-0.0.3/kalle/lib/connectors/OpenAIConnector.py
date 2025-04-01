# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys
import random
import time
import json

from openai import OpenAI, BadRequestError, InternalServerError, AuthenticationError

from kalle.domain.ModelConfig import ModelParam
from kalle.domain.Constrainer import Constrainer, ConstrainerType
from . import LLMConnector


class OpenAIConnector(LLMConnector.LLMConnector):

  def __init__(self, config, /, **kwargs):
    super().__init__(config, **kwargs)
    self.setup_client()

  def setup_client(self):
    if self.config:
      self.client = OpenAI(
          base_url=self.config["url"],
          api_key=self.config["api_key"],
      )

  async def request(
      self,
      /,
      system_prompt: str,
      messages: list[dict],
      model_params: list[ModelParam] | None = None,
      constrainer: Constrainer | None = None,
      **kwargs,
  ) -> str | None:
    tries = 0

    while tries < self.config["retry_max"]:
      tries += 1
      current_delay = (
          self.config["retry_delay"]
          * self.config["retry_exponential_base"]
          * (1 + self.config["jitter"] * random.random())
      )
      try:
        params = self.gen_params(model_params)

        if constrainer is not None and constrainer.type == ConstrainerType("jsonschema"):
          params["response_format"] = {
              "type": "json_schema",
              "json_schema": {
                  "name": "schema",  # this isn't relevant to our use
                  "strict": True,
                  "schema": json.loads(constrainer.value),
              },
          }

        completion = self.client.chat.completions.create(
            model=self.model or self.config["model"],
            messages=[{"role": "system", "content": system_prompt}] + messages,  # type: ignore
            **params,
        )

        response_text = completion.choices[0].message.content
        return response_text

      except AuthenticationError as e:
        errstr = e.body or "UNKNOWN AUTH ERROR"
        if isinstance(e.body, dict):
          errstr = e.body.get("message", "UNKNOWN AUTH ERROR")
        self.console_stderr.print(
            f"\n[red][bold]There was an issue authenticating with OpenAI's API:[/bold] {str(errstr)}"
        )
        sys.exit(64)

      except BadRequestError as e:
        self.console_stderr.print(f"\n[red][bold]There was an issue with the request:[/bold] {e}")
        sys.exit(65)

      except InternalServerError as e:
        if self.debug:
          if e.message == "Error code: 502":
            self.console_stderr.print(f"[red]The OpenAI API server {self.client.base_url} is unreachable.")
          else:
            self.console_stderr.print(f"[red]An exception occurred try {tries} sleeping for {current_delay} {e=}")
            self.console_stderr.print_exception(show_locals=True)
        pass
      except Exception as e:
        if self.debug:
          self.console_stderr.print(f"[red]An exception occurred try {tries} sleeping for {current_delay} {e=}")
          self.console_stderr.print_exception(show_locals=True)
        pass

      time.sleep(current_delay)

    return None
