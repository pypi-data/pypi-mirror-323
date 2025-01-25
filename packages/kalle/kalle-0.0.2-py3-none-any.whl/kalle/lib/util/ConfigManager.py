# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import os.path
import sys

import yaml
import json
import functools
from jsonschema import validate, ValidationError
from typing import Optional
from platformdirs import user_config_dir, user_data_dir, user_cache_dir

from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule

console_stderr = Console(file=sys.stderr)


def find_conversation_key(start_dir):
  path = start_dir or os.getcwd()
  expanded_path = os.path.expanduser(path)
  directories = expanded_path.split(os.path.sep)

  while len(directories) > 0:
    conversation_file = functools.reduce(lambda x, y: os.path.join(x, y), ["/", *directories, ".kalle_conversation"])
    if os.path.exists(conversation_file):
      with open(conversation_file) as f:
        return f.readline().strip()
    directories.pop()
  return None


def validate_config(kalle_root: str, config: dict, /, config_file_path: str, debug: bool = False) -> [bool, str]:
  try:
    # get the schema
    schema_path = os.path.join(kalle_root, "kalle/schema/config-schema.json")
    with open(schema_path) as f:
      schema = json.load(f)

    # validate!
    validate(instance=config, schema=schema)
    return {True, None}
  except ValidationError as e:
    console_stderr.print(
        Panel(
            Group(
                f"[bold]CONFIG LOCATION:[/bold] {config_file_path}",
                Rule(style="red"),
                str(e),
            ),
            title="[red bold]CONFIGURATION PROBLEM",
            style="red",
        )
    )
    if debug:
      console_stderr.print_exception(show_locals=True)
    sys.exit(110)


class ConfigManager:

  def __init__(
      self,
      appname,
      appauthor,
      /,
      base_file_dir: str,
      conversation_key: Optional[str] = None,
      use_memory: bool = True,
      format_output: Optional[bool] = None,
      debug: bool = False,
  ):
    self._appname = appname
    self._appauthor = appauthor
    self._conversation_key = conversation_key if use_memory else None
    self._use_memory = use_memory
    self._format_output = format_output
    self._debug = debug

    config_dir = user_config_dir(appname, appauthor)
    config_file_path = os.environ.get("KALLE_CONFIG") or f"{config_dir}/config.yml"
    self.kalle_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))

    if not os.path.exists(config_file_path):
      import shutil

      shutil.copy(os.path.join(self.kalle_root, "kalle/data/config.yml.example"), config_file_path)
      console_stderr.print(f"[orange1]Configuration file is missing {config_file_path}. [green]New config created.")
      # sys.exit(111)
      # return  # needed for mocking of sys.exit in tests

    with open(config_file_path) as file:
      try:
        self.yaml_config = yaml.safe_load(file)
      except Exception as e:
        console_stderr.print(
            f"[red][bold]Configuration file [italic]{config_file_path}[/italic] is invalid:[/bold]\n{e}"
        )
        sys.exit(112)
        return  # needed for mocking of sys.exit in tests

      validate_config(self.kalle_root, self.yaml_config, config_file_path=config_file_path, debug=debug)

      from kalle.domain.Config import Config
      from kalle.domain.Profile import Profile
      from kalle.domain.Pattern import Pattern
      from kalle.domain.Constrainer import Constrainer, ConstrainerType
      from kalle.domain.PromptTemplate import PromptTemplate
      from kalle.domain.Connector import connector_factory
      from kalle.domain.ModelConfig import ModelConfig, ModelLocationType, ModelParam

      profiles = {}
      for k in self.yaml_config["profiles"].keys():
        model_params = []
        if "model_params" in self.yaml_config["profiles"][k]:
          for p in self.yaml_config["profiles"][k]["model_params"].keys():
            model_params.append(ModelParam(key=p, value=self.yaml_config["profiles"][k]["model_params"][p]))
        profiles[k] = Profile(
            key=k,
            name=self.yaml_config["profiles"][k].get("name", k),
            model=self.yaml_config["profiles"][k]["model"],
            connector=connector_factory(self.yaml_config["profiles"][k]["connector"]).model_validate(
                self.yaml_config["profiles"][k]["connector"]
            ),
            model_params=model_params,
        )
        profiles[k].connector.key = self.find_api_key(k)

      models_map = {}
      for k in self.yaml_config["models_map"].keys():
        models_map[k] = {}
        for k2 in self.yaml_config["models_map"][k].keys():
          model_map_params = []
          if "params" in self.yaml_config["models_map"][k][k2]:
            for p in self.yaml_config["models_map"][k][k2]["params"].keys():
              model_map_params.append(ModelParam(key=p, value=self.yaml_config["models_map"][k][k2]["params"][p]))

          models_map[k][k2] = ModelConfig(
              key=k2,
              name=self.yaml_config["models_map"][k][k2].get("name", None),
              location=ModelLocationType(self.yaml_config["models_map"][k][k2]["location"]),
              model=self.yaml_config["models_map"][k][k2].get("model", None),
              tokenizer=self.yaml_config["models_map"][k][k2].get("tokenizer", None),
              context_size=self.yaml_config["models_map"][k][k2].get("context_size", 1024),
              path=self.yaml_config["models_map"][k][k2].get("path", None),
              repo_id=self.yaml_config["models_map"][k][k2].get("repo_id", None),
              filename=self.yaml_config["models_map"][k][k2].get("filename", None),
              publisher=self.yaml_config["models_map"][k][k2].get("publisher", None),
              params=model_map_params,
          )

      prompt_templates = {}
      for k in self.yaml_config["prompts"].keys():
        prompt_templates[k] = PromptTemplate(
            key=k,
            name=k,
            value=self.yaml_config["prompts"][k],
        )

      patterns = {}
      patterns_dir = self.patterns_dir
      if os.path.exists(patterns_dir):
        for filename in os.listdir(patterns_dir):
          try:
            if filename.endswith(".yaml"):
              pattern_key = filename[:-5]
              pattern_file_path = os.path.join(patterns_dir, filename)
              with open(pattern_file_path) as file:
                pattern_yaml = yaml.safe_load(file)

                system_prompt_template = None
                if "system_prompt_template" in pattern_yaml:
                  system_prompt_template = PromptTemplate(
                      key="system_prompt_template", value=pattern_yaml["system_prompt_template"]
                  )

                prompt_template = None
                if "prompt_template" in pattern_yaml:
                  prompt_template = PromptTemplate(key="prompt_template", value=pattern_yaml["prompt_template"])

                constrainer = None
                if (
                    "constrainer" in pattern_yaml
                    and type(pattern_yaml["constrainer"]) is dict
                    and "type" in pattern_yaml["constrainer"]
                ):
                  constrainer = Constrainer(
                      type=ConstrainerType(pattern_yaml["constrainer"]["type"]),
                      value=pattern_yaml["constrainer"]["value"],
                  )

                profile = None
                if "profile" in pattern_yaml and pattern_yaml["profile"] in profiles.keys():
                  profile = profiles[pattern_yaml["profile"]]

                patterns[pattern_key] = Pattern(
                    key=pattern_key,
                    name=pattern_yaml.get("name", None),
                    system_prompt_template=system_prompt_template,
                    prompt_template=prompt_template,
                    tools=pattern_yaml.get("tools", None),
                    constrainer=constrainer,
                    profile=profile,
                )
          except Exception as e:
            if self.debug:
              console_stderr.print(f"[orange1]Pattern {filename} is invalid, skipping: {e}")

      # We only have a conversation key if we're using memory
      if use_memory:
        if conversation_key is None:
          # Look for a configured file-based conversation key
          found_conversation_key = find_conversation_key(base_file_dir)

          # check for an embedded contextual key via a `.kalle_conversation` file
          if found_conversation_key:
            console_stderr.print(f"[yellow]USING FOUND CONVERSATION CONTEXT: {found_conversation_key}")
            conversation_key = found_conversation_key.strip()
          else:
            # use the configured default if available
            conversation_key = self.yaml_config.get("default_conversation", None)

        self._conversation_key = conversation_key

      self.config = Config(
          appname=appname,
          appauthor=appauthor,
          conversation_key=conversation_key,
          use_memory=use_memory,
          debug=debug,
          profiles=profiles,
          patterns=patterns,
          models_map=models_map,
          prompt_templates=prompt_templates,  # Can this be pushed fully into patterns as default patterns?
      )

  # #####################################################
  # Directories
  @property
  def config_dir(self) -> str | None:
    kalle_config = user_config_dir(self._appname, self._appauthor)
    if os.environ.get("KALLE_CONFIG", None) is not None:
      kalle_config = os.path.dirname(os.environ.get("KALLE_CONFIG", None))  # type: ignore

    return kalle_config

  @property
  def data_dir(self):

    return os.environ.get("KALLE_DATA_DIR", None) or self.yaml_config.get(
        "data_dir", user_data_dir(self._appname, self._appauthor)
    )

  @property
  def cache_dir(self):
    return os.environ.get("KALLE_CACHE_DIR", None) or self.yaml_config.get(
        "cache_dir", user_cache_dir(self._appname, self._appauthor)
    )

  @property
  def patterns_dir(self):
    return os.environ.get("PATTERNS_DIR", None) or self.yaml_config.get(
        "patterns_dir", os.path.join(self.kalle_root, "patterns")
    )

  # #####################################################
  # Debug
  @property
  def debug(self):
    return self._debug

  # #####################################################
  # Memory
  @property
  def use_memory(self):
    return self._use_memory

  # #####################################################
  # Format Output
  @property
  def format_output(self):
    return self._format_output if self._format_output is not None else self.yaml_config.get("format_output", False)

  @property
  def interactive_style(self):
    return self.yaml_config.get("interactive_style", "plain")

  # #####################################################
  # Conversation
  @property
  def conversation_key(self):
    return self._conversation_key

  # #####################################################
  # API Keys
  def find_api_key(self, profile_name):
    api_key = self.yaml_config.get("profiles", {}).get(profile_name, {}).get("connector", {}).get("key")
    if api_key is None and os.path.isfile(f"{self.config_dir}/{profile_name}.key"):
      with open(f"{self.config_dir}/{profile_name}.key") as file:
        api_key = file.read().replace("\n", "")

    return api_key

  # #####################################################
  # Google App Credentials File
  @property
  def google_app_credentials_path(self):
    return self.yaml_config.get("google_app_credentials_path", None)

  # #####################################################
  # CONVERSATIONS
  @property
  def conversation_dir(self):
    return os.path.normpath(f"{self.data_dir}/conversations/")

  # ###################################################################################################################
  # From config file

  # #####################################################
  # profiles
  @property
  def profiles(self):
    return self.config.profiles

  # #####################################################
  # patterns
  @property
  def patterns(self):
    return self.config.patterns

  # #####################################################
  # Models Map
  @property
  def models_map(self):
    return self.config.models_map

  # #####################################################
  # Prompts
  @property
  def prompts(self):
    from kalle.domain.PromptTemplate import PromptTemplate

    return self.config.prompt_templates or {
        "kalle_system_prompt": PromptTemplate(
            key="kalle_system_prompt",
            value="Your name is Kalle. You are a helpful, confident and friendly personal assistant.",
        ),
        "base_tool_prompt": PromptTemplate(
            key="base_tool_prompt",
            value="",
        ),
    }
