# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys

from rich.console import Console

from kalle.lib.tokenizers.BaseTokenizer import BaseTokenizer
from kalle.lib.util.Tokenizers import Tokenizers
from kalle.domain.ModelConfig import ModelConfig, ModelParam


class LLMConnector:
  """
  A connector class for Large Language Models (LLMs).

  This class provides a basic structure for connecting to LLMs and making
  requests to models available via that connection. These could be direct via
  code, locally hosted or third party APIs.
  """

  def __init__(
      self,
      config,
      /,
      models_map: dict[str, ModelConfig],
      model: str | None = None,
      console_stderr: Console | None = None,
      debug: bool = False,
  ):
    """
    Initializes the LLMConnector object.

    Args:
        config (dict): The configuration dictionary for the connector.
        models_map (dict): A dictionary mapping model names to their configurations.
        model (str, optional): The name of the model to use. Defaults to None.
        console_stderr (Console, optional): A Console object for printing to stderr. Defaults to None.
        debug (bool, optional): A flag indicating whether to run in debug mode. Defaults to False.
    """
    self.config = config
    self.models_map = models_map
    self.model = model
    self.client = None
    self.llm_tokenizers = Tokenizers(self.config)
    self.tokenizer = None
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    self.debug = debug
    self.setup_client()

  def get_model(self, _model_name=None) -> ModelConfig:
    """
    Gets the model configuration for the given model name.

    Args:
        _model_name (str, optional): The name of the model to get. Defaults to None.

    Returns:
        ModelConfig | None: The model configuration if found, otherwise None.
    """
    model_name = _model_name or self.model or self.config["model"]
    return self.models_map[model_name]

  def get_tokenizer(self, _model_name=None) -> BaseTokenizer:
    """
    Gets the tokenizer for the given model name.

    Args:
        _model_name (str, optional): The name of the model to get. Defaults to None.

    Returns:
        BaseTokenizer | None: The tokenizer if found, otherwise None.
    """
    model_name = _model_name or self.config["model"]
    tokenizer_key = self.get_model(model_name).tokenizer
    return self.llm_tokenizers.get_tokenizer(tokenizer_key, model_name)

  def gen_params(self, model_params: list[ModelParam] | None = None) -> dict:
    """
    Generates a dictionary of parameters from the given model parameters.

    Args:
        model_params (list[ModelParam], optional): The list of model parameters. Defaults to None.

    Returns:
        dict: A dictionary of parameters.
    """
    params = {}
    if model_params is None:
      return {}

    model_map_params = self.get_model().params
    if model_map_params is not None:
      for p in model_map_params:
        params[p.key] = p.value

    for p in model_params:
      params[p.key] = p.value

    return params

  def setup_client(self) -> None:
    """
    Sets up the client for the LLM.

    This method must be implemented by subclasses.
    """
    raise NotImplementedError("Subclasses must implement setup_client method")

  async def request(
      self,
      /,
      system_prompt: str,
      messages: list[dict],
      model_params: list[ModelParam] | None = None,
      **kwargs,
  ) -> str | None:
    """
    Makes a request to the LLM.

    This method must be implemented by subclasses.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The list of messages for the request.
        model_params (list[ModelParam], optional): The list of model parameters. Defaults to None.
        constrainer (Constrainer, optional): The constrainer for the request. Defaults to None.

    Returns:
        str | None: The response from the LLM if successful, otherwise None.
    """
    raise NotImplementedError("Subclasses must implement request method")
