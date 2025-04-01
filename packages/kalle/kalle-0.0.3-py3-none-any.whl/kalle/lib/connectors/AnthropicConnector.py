# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import random
import time
import anthropic

from . import LLMConnector
from kalle.domain.ModelConfig import ModelParam


class AnthropicConnector(LLMConnector.LLMConnector):
  """
  A connector for interacting with the Anthropic API using this library:
  [](https://github.com/anthropics/anthropic-sdk-python)

  This class provides a interface for sending requests to the Anthropic API
  and handling the responses.

  An Anthrropic API account is required. Details can be found here to set one
  up: [](https://docs.anthropic.com/en/docs/initial-setup)
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the AnthropicConnector instance.

    Args:
        config (dict): The configuration for the connector.
        **kwargs: Additional keyword arguments.
    """
    super().__init__(config, **kwargs)

    self.setup_client()

  def setup_client(self):
    """
    Sets up the Anthropic client using the provided configuration. An API
    key is required.
    """
    if self.config:
      self.client = anthropic.Anthropic(
          api_key=self.config["api_key"],
      )

  async def request(
      self,
      /,
      system_prompt: str,
      messages: list[dict],
      model_params: list[ModelParam] | None = None,
      model: str | None = None,
      **kwargs,
  ) -> str | None:
    """
    Sends a request to the Anthropic API.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The messages for the request.
        model (str | None): The model to use for the request. Defaults to None.
        model_params (list[ModelParam] | None): The model parameters for the request. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str | None: The response from the Anthropic API, or None if the request fails.
    """
    tries = 0
    while tries < self.config["retry_max"]:
      tries += 1
      try:
        anthropic_messages = self.convert_messages_to_anthropic(messages)

        params = self.gen_params(model_params)
        params["system"] = system_prompt
        # required by Anthropic
        params["model"] = model or self.model or self.config["model"]
        params["max_tokens"] = params.get("max_tokens", 4096)
        params["messages"] = anthropic_messages

        response = self.client.messages.create(**params)

        resp = response.content[0].text  # type: ignore
        resp = resp.replace("Claude", "Kalle")

        return resp
      except Exception as e:
        # UnprocessableEntityError
        current_delay = (
            self.config["retry_delay"]
            * self.config["retry_exponential_base"]
            * (1 + self.config["jitter"] * random.random())
        )
        if self.debug:
          self.console_stderr.print(f"An exception occurred try {tries} sleeping for {current_delay} {e=}")
        time.sleep(current_delay)

    return None

  def convert_messages_to_anthropic(self, messages):
    """
    Converts the provided messages to the format expected by the Anthropic API.

    Args:
        messages (list[dict]): The messages to convert.

    Returns:
        list[dict]: The converted messages.
    """
    anthropic_messages = []

    for message in messages:
      if message["role"] == "system":
        continue

      role = message["role"]
      content = message["content"]
      anthropic_message = {"role": role, "content": [{"type": "text", "text": content}]}
      anthropic_messages.append(anthropic_message)

    return anthropic_messages
