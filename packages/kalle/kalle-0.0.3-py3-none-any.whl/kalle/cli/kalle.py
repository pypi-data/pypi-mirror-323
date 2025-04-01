# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2

# #############################################################################
# Imports
# #############################################################################
import kalle.cli.sigint_clean_exit  # noqa: F401  Imported for side effect

import argparse
import asyncio
import time

import json
import os
import sys

from typing import Optional
from platformdirs import user_config_dir, user_data_dir, user_cache_dir

from rich.console import Console, Group
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich_argparse import RawDescriptionRichHelpFormatter

# Utilities
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ConversationTools import ConversationTools
from kalle.lib.util.ProfileManager import ProfileManager
from kalle.lib.util.PromptManager import PromptManager

# Domain
from kalle.domain.Conversation import ConversationMessage
from kalle.domain.Context import Context
from kalle.domain.Constrainer import Constrainer
# from kalle.domain.LLMRequest import LLMRequest


class Kalle:

  def __init__(self, /, base_file_dir: Optional[str] = None, debug: bool = False):
    self.appname = "kalle"
    self.appauthor = "fe2"

    self.conversing = False
    self.console = Console()
    self.console_stderr = Console(file=sys.stderr)

    if base_file_dir is None:
      self.base_file_dir = os.getcwd()
    else:
      self.base_file_dir = base_file_dir

    # cache in kalle's cache
    os.environ["TIKTOKEN_CACHE_DIR"] = os.path.join(user_cache_dir(self.appname, self.appauthor), "tiktoken_cache")

    # Suppress non-actionable warnings when using kalle unless we're debugging
    if not debug:
      os.environ["TRANSFORMERS_VERBOSITY"] = "error"
      os.environ["TOKENIZERS_PARALLELISM"] = "false"
      os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
      from transformers.utils import logging

      logging.disable_progress_bar()
      import warnings

      warnings.filterwarnings("ignore")

    # #############################################################################################################
    # load the config
    self.check_dirs()
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        base_file_dir=base_file_dir or os.getcwd(),
        debug=debug,
    )
    self.conversation_tools = ConversationTools(self.config)

  def check_dirs(self):
    # Ensure relevant directories exist
    config_dir = user_config_dir(self.appname, self.appauthor)
    cache_dir = user_cache_dir(self.appname, self.appauthor)
    data_dir = user_data_dir(self.appname, self.appauthor)

    self.check_and_create_dir(config_dir)  # config dir
    self.check_and_create_dir(data_dir)  # data dir
    self.check_and_create_dir(os.path.join(data_dir, "conversations"))  # conversations dir
    self.check_and_create_dir(cache_dir)  # cache dir
    self.check_and_create_dir(os.path.join(cache_dir, "tiktoken_cache"))  # tiktoken cache dir
    self.check_and_create_dir(os.path.join(cache_dir, "tokens"))  # tokens cache dir

  def check_and_create_dir(self, dir_path):
    if not os.path.exists(dir_path):
      try:
        os.makedirs(dir_path)
      except Exception:
        self.console_stderr.print(f"[red]Could not create {dir_path} directory")

  def show_history(self, conversation_key: Optional[str] = None):
    if conversation_key is None:
      self.console_stderr.print("[red]NO CONVERSATION TO SHOW HISTORY FOR")
      return

    self.console.print(f"[bold magenta]CONVERSATION HISTORY FOR: [italic]{conversation_key}")
    conversation = self.conversation_tools.load_conversation(conversation_key)
    ac = ""
    al = "center"
    for c in conversation.get_messages():
      ac = "blue"
      al = "right"
      name = "User"
      if c["role"] == "assistant":
        ac = "orange1"
        al = "left"
        name = "kalle"
      self.console.print(Panel(f"[{ac}]{c['content']}", subtitle=f"[{ac} bold]< {name} >", subtitle_align=al, style=ac))

  def list_conversations(self):
    conversations = self.conversation_tools.list_conversations()
    self.console_stderr.print("[bold magenta]CONVERSATIONS:")
    for c in conversations:
      self.console.print(f"{c}", highlight=False)

  def handle_inline_commands(self, text: Optional[str] = None):
    if text is None:
      return

    if text.startswith("reset conversation"):
      if self.context.use_memory and self.context.conversation_key is not None and self.conversation.conversation != []:
        self.conversation_tools.archive_conversation()

        self.console.print("[green]Conversation reset")
        sys.stdout.flush()
        sys.exit(0)
      else:
        self.console.print("[dark_orange]No conversation to reset")
        sys.stdout.flush()
        sys.exit(0)

    if text.startswith("set conversation"):
      conversation_name = text.split("set conversation ")[1].strip()
      conversation_file_path = os.path.join(self.base_file_dir, ".kalle_conversation")

      if os.path.exists(conversation_file_path):
        self.console_stderr.print(
            f"[red]Warning: A conversation file already exists at {conversation_file_path}, not overwriting."
        )
        sys.exit(27)
      else:
        with open(conversation_file_path, "w") as f:
          f.write(conversation_name)
        self.console.print(
            f"[green]Conversation file created at {conversation_file_path} for conversation {conversation_name}"
        )
      sys.exit(0)

    if text.startswith("unset conversation"):
      conversation_file_path = os.path.join(self.base_file_dir, ".kalle_conversation")

      try:
        os.remove(conversation_file_path)
        self.console.print(f"[green]Conversation file removed at {conversation_file_path}")
      except FileNotFoundError:
        self.console_stderr.print(f"[red]File not found to remove at {conversation_file_path}")
        sys.exit(28)
      except Exception as e:
        self.console_stderr.print(f"[red]An error occurred removing conversation file {conversation_file_path}: {e}")
        sys.exit(29)

      sys.exit(0)

  def load_pattern(self, pattern_key: str):
    if pattern_key is not None:
      if pattern_key in self.config.patterns:
        return self.config.patterns[pattern_key]
      else:
        self.console_stderr.print(f"[red]Pattern '{pattern_key}' is not found.")
        exit(17)

  def show_debug_info(self):
    if self.config.debug:
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]USE MEMORY:[/bold] {self.context.use_memory}",
                  f"[magenta][bold]FORMAT OUTPUT:[/bold] {self.config.format_output}",
                  f"[magenta][bold]CONVERSATIONS:[/bold] {len(self.conversation_tools.list_conversations())}",
              ),
              title="[bold magenta]GENERAL DEBUG INFO",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]CONVERSATION KEY:[/bold] {self.config.conversation_key}",
                  f"[magenta][bold]CONVERSATION ENTRIES:[/bold] {len(self.conversation.conversation) - 1}",
              ),
              title="[bold magenta]CONVERSATION",
              style="magenta",
          )
      )

      model_tree = Tree(f"[magenta][bold]MODEL:[/bold] {type(self.profile_manager.model)}")
      model_tree.add(f"[magenta][bold]MODEL_STRING:[/bold] {self.profile_manager.model.name}")
      model_tree.add(f"[magenta][bold]CONTEXT_SIZE:[/bold] {self.profile_manager.model.context_size}")
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]PROFILE:[/bold] {self.profile_manager.profile.key}",
                  f"[magenta][bold]CONNECTOR:[/bold] {type(self.profile_manager.connector)}",
                  model_tree,
              ),
              title="[bold magenta]PROFILE",
              style="magenta",
          )
      )

      pattern_tree = Tree(f"[magenta][bold]PATTERN:[/bold] {self.context.args_pattern_key}")
      pattern_tree.add(f"[magenta][bold]NAME:[/bold] {self.pattern.name if self.pattern is not None else None}")
      self.console_stderr.print(
          Panel(
              Group(
                  pattern_tree,
              ),
              title="[bold magenta]PATTERN",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.context.args_system_prompt}",
              ),
              title="[magenta]ARGS SYSTEM PROMPT",
              style="magenta",
          )
      )

      config_system_prompt = self.config.prompts.get("kalle_system_prompt", None)
      config_system_prompt = config_system_prompt.value if config_system_prompt is not None else None
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{config_system_prompt}",
              ),
              title="[magenta]CONFIG SYSTEM PROMPT",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"""[magenta][bold]PATTERN Constrainer:[/bold]
  [bold]TYPE:[/bold] {self.pattern.constrainer.type if self.pattern is not None and self.pattern.constrainer is not None else None}
  [bold]VALUE:[/bold] {self.pattern.constrainer.value if self.pattern is not None and self.pattern.constrainer is not None else None}
""",
              ),
              title="[magenta]CONSTRAINER",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.pattern.system_prompt_template if self.pattern is not None else None}",
              ),
              title="[magenta]PATTERN SYSTEM PROMPT TEMPLATE",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.conversation.metadata.system_prompt if self.conversation.metadata is not None else None}",
              ),
              title="[magenta]CONVERSATION SYSTEM PROMPT",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT_TOKEN_COUNT (approximate):[/bold] {self.system_prompt_tokens}",
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.system_prompt}",
              ),
              title="[bold magenta]FINAL SYSTEM PROMPT",
              style="magenta",
          )
      )

      tools = []
      if self.tool_handler is not None:
        for t, _ in self.tool_handler.get_tools().items():
          tools.append(f"[magenta]- {t}")

        self.console_stderr.print(
            Panel(
                Group(
                    *tools,
                ),
                title="[bold magenta]TOOLS",
                style="magenta",
            )
        )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]PROMPT_TOKEN_COUNT (approximate):[/bold] {self.prompt_tokens}",
                  "[magenta][bold]PROMPT:[/bold]",
                  Syntax(json.dumps(self.compiled_prompt, indent=4), "json", word_wrap=True),
              ),
              title="[bold magenta]PROMPT",
              style="magenta",
          )
      )

  def llm_request_status_line(self) -> str:
    conv_disp = ""
    if self.context.conversation_key is not None:
      conv_disp = f" (CONVERSATION: [italic]{self.context.conversation_key}[/italic])"

    status_line = f"[bold yellow]Making LLM request ({self.profile_manager.profile.connector.name}/{self.profile_manager.model.key}){conv_disp}..."

    return status_line

  async def run(
      self,
      /,
      param_content: str,
      piped_content: Optional[str] = None,
      use_memory: bool = False,
      constrainer: Optional[Constrainer] = None,
      interactive: bool = False,
      format_output: bool = True,
      conversation_key: Optional[str] = None,
      args_system_prompt: Optional[str] = None,
      args_profile_key: Optional[str] = None,
      args_pattern_key: Optional[str] = None,
      args_model_params: Optional[list] = None,
      follow_uris: bool = False,
      tool_list: Optional[list] = None,
      use_tools: bool = False,
      args_model_string: Optional[str] = None,
      debug: bool = False,
  ):

    self.interactive = interactive
    self.format_output = format_output
    self.context = Context(
        base_file_dir=self.base_file_dir,
        use_memory=use_memory,
        param_content=param_content,
        piped_content=piped_content,
        conversation_key=conversation_key,
        args_system_prompt=args_system_prompt,
        args_profile_key=args_profile_key,
        args_pattern_key=args_pattern_key,
        args_model_string=args_model_string,
        args_model_params=args_model_params,
        constrainer=constrainer,
        follow_uris=follow_uris,
        tool_list=tool_list,
        use_tools=use_tools or False,
        debug=debug,
    )

    content = self.context.param_content

    # #############################################################################################################
    # load the config
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=self.context.conversation_key,
        base_file_dir=self.base_file_dir,
        use_memory=self.context.use_memory,
        format_output=self.format_output,
        debug=self.context.debug,
    )
    self.conversation_tools = ConversationTools(self.config)

    # #############################################################################################################
    # load a pattern (if specified)
    self.pattern = self.load_pattern(self.context.args_pattern_key) if self.context.args_pattern_key else None

    # #############################################################################################################
    # set up things that depend on the config

    # set the active profile key
    self.profile_key = None
    if self.context.args_profile_key is not None:
      if self.context.args_profile_key in self.config.profiles.keys():
        self.profile_key = self.context.args_profile_key
      else:
        self.console_stderr.print(f"[red]Profile {self.context.args_profile_key} is not found")
        sys.exit(8)

    # set the URI handler if needed
    self.uri_handler = None
    if self.context.follow_uris:
      from kalle.lib.util.URIHandler import URIHandler

      self.uri_handler = URIHandler(self.config, self.base_file_dir)

    # set the tool handler if needed
    self.tool_handler = None
    if self.context.use_tools:
      from kalle.lib.util.ToolHandler import ToolHandler

      self.tool_handler = ToolHandler(
          self.config,
          base_file_dir=self.base_file_dir,
          tool_list=self.context.tool_list,
          console_stderr=self.console_stderr,
      )

    # #############################################################################################################
    # load the stored conversation
    if self.context.conversation_key is not None:
      self.conversation = self.conversation_tools.load_conversation(self.context.conversation_key)

    # set up an empty one if a conversation key isn't specified
    if not hasattr(self, "conversation"):
      self.conversation = self.conversation_tools.empty_conversation

    # reset the conversation if one is active
    self.handle_inline_commands(self.context.param_content)

    # #############################################################################################################
    # load the profile (connection and model)
    # look for the profile key in:
    # - a passed conversation key
    # - the conversation metadata
    conversation_profile_key = None
    if self.conversation.metadata.profile is not None:
      conversation_profile_key = self.conversation.metadata.profile.key

    if self.pattern is not None and self.pattern.profile is not None:
      self.profile_key = self.pattern.profile.key
    self.profile_key = self.profile_key or conversation_profile_key or "base"

    self.profile_manager = ProfileManager(
        self.config, self.profile_key, model_string=self.context.args_model_string, console_stderr=self.console_stderr
    )

    # prepare the system, user prompts
    prompt_manager = PromptManager(
        self.config,
        system_prompt_template=self.pattern.system_prompt_template if self.pattern else None,
        system_prompt=self.context.args_system_prompt,
        prompt_template=self.pattern.prompt_template if self.pattern else None,
        piped_content=self.context.piped_content,
        param_content=self.context.param_content,
    )

    self.system_prompt = prompt_manager.compile_system_prompt()
    content = prompt_manager.compile_prompt()

    # parse and unroll URIs
    (compiled_content, _) = (
        self.uri_handler.parse_content(content)
        if self.uri_handler is not None and self.context.follow_uris
        else (content, None)
    )

    # add the compiled content to the message for the llm
    current_conversation_message = ConversationMessage(
        timestamp=time.time(),
        profile=self.profile_manager.profile,
        system_prompt=self.context.args_system_prompt,
        role="user",
        piped_content=self.context.piped_content,
        param_content=self.context.param_content,
        content=compiled_content,
    )

    historic_conversation = self.conversation.get_messages()
    current_prompt = current_conversation_message.get_message()

    # add the current message to the conversation
    self.conversation.conversation.append(current_conversation_message)

    # prompt to send to the LLM
    self.compiled_prompt = []

    # add the conversation if we're permitting conversation memory
    if self.config.use_memory or self.interactive:
      self.compiled_prompt += historic_conversation

    self.compiled_prompt += (current_prompt,)

    if self.profile_manager.model is None:
      self.console_stderr.print(f"[red]Error: Model not available in models_map {self.profile_manager.profile.model}")
      sys.exit(18)

    self.system_prompt_tokens = self.profile_manager.tokenizer.get_conversation_tokens(
        [{"role": "system", "content": self.system_prompt}]
    )
    self.prompt_tokens = self.profile_manager.tokenizer.get_conversation_tokens(self.compiled_prompt)

    # self.llm_request = LLMRequest(
    #        key = "",
    #        system_prompt = "",
    #        piped_prompt = "",
    #        args_prompt = "",
    #        tools = "",
    #        constrainer = "",
    #        connector = "",
    #        model = "",
    #    )

    # constrainer if one is available
    constrainer = self.context.constrainer or (self.pattern.constrainer if self.pattern is not None else None)

    self.show_debug_info()

    response = ""
    tool_prompt = None
    tool_response = None
    if self.system_prompt_tokens + self.prompt_tokens > self.profile_manager.model.context_size - 100:
      self.console_stderr.print(
          f"[red]Warning: length of prompt exceeds the current max context length ({self.profile_manager.model.context_size}), aborting."
      )
      sys.exit(9)
    else:
      # fetch a response
      if self.context.use_tools:
        # compile the system prompt specific to the available tools
        compiled_tool_prompt = prompt_manager.compile_tool_prompt(
            self.tool_handler.get_tools() if self.tool_handler is not None else None
        )
        tool_prompt = compiled_tool_prompt

        if self.config.debug:
          self.console_stderr.print(
              Panel(f"[magenta]{compiled_tool_prompt}", title="[bold magenta]COMPILED TOOL PROMPT", style="magenta")
          )

        tool_prompt_message = {
            "role": "user",
            "content": f"{self.compiled_prompt[-1]['content']}\n{compiled_tool_prompt}",
        }

        with self.console_stderr.status("[bold yellow]Making tool request..."):
          from kalle.domain.ModelConfig import ModelParam

          tool_response = await self.profile_manager.connector.request(
              self.system_prompt,
              self.compiled_prompt[0:-2] + [tool_prompt_message],
              model_params=[ModelParam(key="temperature", value=0.1)],
          )

        if self.config.debug:
          self.console_stderr.print(
              Panel(f"[magenta]{tool_response}", title="[bold magenta]TOOLING RESPONSE", style="magenta")
          )

        # invoke the tools returned by the preliminary response and compile into another llm request
        tooled_request = ""
        if tool_response is not None:
          with self.console_stderr.status("[bold yellow]Processing tool calls..."):
            tooled_request = self.tool_handler.process(tool_response) if self.tool_handler is not None else ""
            tooled_request += f"\n\n---\nThis was the original user request and the content before this message is the results of a set of tool calls that you performed:\n{self.compiled_prompt[-1]['content']}"

        if tooled_request is None or tooled_request == "":
          tooled_request = "Report to the user that you ran into an internal issue completing the user's request and ask the user to try again. Don't make any promises."

        # make the final request to the llm
        with self.console_stderr.status(self.llm_request_status_line()):
          response = await self.profile_manager.connector.request(
              system_prompt=self.system_prompt,
              messages=[{"role": "user", "content": tooled_request}],
              model_params=self.profile_manager.profile.model_params,
              constrainer=constrainer,
          )
      else:
        # make the request to the llm
        with self.console_stderr.status(self.llm_request_status_line()):
          response = await self.profile_manager.connector.request(
              system_prompt=self.system_prompt,
              messages=self.compiled_prompt,
              model_params=self.profile_manager.profile.model_params,
              constrainer=constrainer,
          )

    if not response:
      self.console_stderr.print("[red]AN ERROR OCCURRED WHILE AWAITING A RESPONSE")
      sys.exit(10)

    # conversation.metadata.system_prompt = self.system_prompt
    self.conversation.metadata.profile = self.profile_manager.profile
    self.conversation.conversation.append(
        ConversationMessage(
            timestamp=time.time(),
            profile=self.profile_manager.profile,
            role="assistant",
            tool_prompt=tool_prompt,
            tool_response=tool_response,
            content=response,
        )
    )
    if self.config.use_memory:
      self.conversation_tools.persist_conversation(self.conversation, conversation_key=self.context.conversation_key)

    if self.config.format_output:
      if self.interactive and self.config.interactive_style != "plain":
        self.console.print(
            Panel(
                Markdown(f"{response}"),
                subtitle="[bold]< Kalle >",
                subtitle_align="left",
                border_style="orange1",
            )
        )
      else:
        self.console.print(Markdown(f"{response}"))
    else:
      self.console.print(f"{response}", highlight=None)

    sys.stdout.flush()


def load_json_schema(kalle: Kalle, jsonschema_path: str):
  jsonschema_path = os.path.expanduser(jsonschema_path)
  if not jsonschema_path.startswith("/"):
    jsonschema_path = os.path.join(kalle.base_file_dir, jsonschema_path)
  try:
    with open(jsonschema_path, "r") as f:
      return json.dumps(json.loads(f.read()))
  except FileNotFoundError:
    kalle.console_stderr.print(f"[red]Could not find JSON schema {jsonschema_path}")
    sys.exit(31)
  except IsADirectoryError:
    kalle.console_stderr.print(f"[red]Specified JSON schema path '{jsonschema_path}' is a directory")
    sys.exit(32)
  except json.decoder.JSONDecodeError as e:
    kalle.console_stderr.print(f"[red]Invalid JSON schema '{jsonschema_path}': {e}")
    sys.exit(33)
  except Exception as e:
    kalle.console_stderr.print(f"[red]Unspecified error loading JSON schema '{jsonschema_path}': {e}")
    sys.exit(34)


def parse_args():
  parser = argparse.ArgumentParser(
      prog="kalle",
      description="[yellow]I'm Kalle! A smart cli friend",
      formatter_class=RawDescriptionRichHelpFormatter,
  )
  RawDescriptionRichHelpFormatter.styles["argparse.prog"] = "yellow"

  parser.add_argument("-l", "--list_conversations", action="store_true", help="List conversations")
  parser.add_argument("-c", "--conversation", type=str, default=None, help="Use a specific conversation")
  parser.add_argument(
      "-i",
      "--interactive",
      action="store_true",
      help="Have an interactive conversation (don't return immediately to the prompt)",
  )
  parser.add_argument("-H", "--history", action="store_true", help="Show the conversation history")
  parser.add_argument("-x", "--nomemory", action="store_true", help="Don't include the conversation memory")
  parser.add_argument("-z", "--unformat", action="store_true", help="Remove output formatting")
  parser.add_argument("-s", "--system_prompt", type=str, help="Override the default system prompt")
  parser.add_argument(
      "-f",
      "--follow",
      action="store_true",
      help="Follow [grey58]http(s)://[/grey58] and [grey58]file://[/grey58] URIS and include their contents",
  )

  parser.add_argument(
      "-J",
      "--jsonschema",
      type=str,
      help="Specifiy the path to a JSON schema to constrain the output [italic](TabbyAPI, Llama.cpp, Ollama only)[/italic]",
  )
  parser.add_argument(
      "-R", "--regex", type=str, help="Specifiy a regex to constrain the output [italic](TabbyAPI)[/italic]"
  )
  parser.add_argument("-D", "--dir", type=str, help="Base dir for [grey58]file:://[/grey58] URIs")

  parser.add_argument("-P", "--profile", type=str, default=None, help="Set the profile to use")
  parser.add_argument("-b", "--base", action="store_true", help="Use the [grey58]base[/grey58] profile")
  parser.add_argument("-.", "--tiny", action="store_true", help="Use the [grey58]tiny[/grey58] profile")
  parser.add_argument("-C", "--code", action="store_true", help="Use the [grey58]code[/grey58] profile")
  parser.add_argument("-X", "--tabbyapi", action="store_true", help="Use [grey58]TabbyAPI[/grey58]")
  parser.add_argument("-o", "--ollama", action="store_true", help="Use [grey58]Ollama[/grey58]")
  parser.add_argument("-A", "--anthropic", action="store_true", help="Use [grey58]Anthropic's[/grey58] API")
  parser.add_argument("-O", "--openai", action="store_true", help="Use [grey58]OpenAI[/grey58] API")
  parser.add_argument("-G", "--groq", action="store_true", help="Use [grey58]Groq[/grey58] API")
  parser.add_argument("-V", "--vertexai", action="store_true", help="Use [grey58]Google VertexAI[/grey58] API")

  parser.add_argument("-p", "--pattern", type=str, default=None, help="Set the pattern to use")

  parser.add_argument(
      "-t",
      "--tool",
      default=None,
      nargs="*",
      type=str,
      help="Enable tool calling with optional comma separated values (e.g., tool1,tool2)",
  )

  parser.add_argument("-m", "--model", type=str, help="Model to use (if applicable)")
  parser.add_argument("-T", "--temp", type=str, help="Temperature to use for the model")
  parser.add_argument("-S", "--seed", type=str, help="Seed to use for inference (if applicable)")
  parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
  parser.add_argument("prompt", nargs=argparse.REMAINDER, help="The message for [yellow]kalle[/yellow]")

  parser.epilog = f"[bold cyan]Config directory:[/bold cyan] [grey58]{user_config_dir('kalle', 'fe2')}\n"
  parser.epilog += f"[bold cyan]Data directory:[/bold cyan] [grey58]{user_data_dir('kalle', 'fe2')}\n"
  parser.epilog += (
      f"[bold cyan]Conversations directory:[/bold cyan] [grey58]{user_data_dir('kalle', 'fe2')}/conversations\n"
  )
  parser.epilog += f"[bold cyan]Cache directory:[/bold cyan] [grey58]{user_cache_dir('kalle', 'fe2')}/conversations"

  return parser.parse_args()


def process_args(**kwargs):
  # map args to vars
  param_content = " ".join(kwargs.get("prompt", []))
  param_content = param_content.lstrip("-- ")
  return {
      "use_memory": not kwargs.get("nomemory", False),
      "interactive": kwargs.get("interactive", None),
      "format_output": not kwargs.get("unformat", False),
      "conversation_key": kwargs.get("conversation", None),
      "args_system_prompt": kwargs.get("system_prompt", None),
      "args_profile_key": kwargs.get("profile", None),
      "args_pattern_key": kwargs.get("pattern", None),
      "follow_uris": kwargs.get("follow", False),
      "tool_list": kwargs.get("tool", None),
      "use_tools": True if kwargs.get("tool", None) is not None else False,
      "args_model_string": kwargs.get("model", None),
      "debug": kwargs.get("debug", False),
      "param_content": param_content,
  }


def cli():
  args = parse_args()
  debug = args.debug
  kalle = Kalle(base_file_dir=args.dir)

  param_content = " ".join(args.prompt)
  param_content = param_content.lstrip("-- ")

  # Check if data is piped in
  piped_content = None
  if not sys.stdin.isatty():
    piped_content = sys.stdin.read()

  try:
    # #############################################################################################################
    # Do things that can cause us to exit early

    # if we're just listing conversations, do that and exit early
    if args.list_conversations:
      kalle.list_conversations()
      sys.exit(0)

    # show history and exit early
    if args.history:
      kalle.show_history(args.conversation)
      sys.exit(0)

    # exit early if we've specified multiple constrainer types
    if args.regex is not None and args.jsonschema is not None:
      kalle.console_stderr.print("[red]Specify only one of JSON schema or regex")
      sys.exit(2)

    # exit early if we haven't specified a request
    if param_content == "" and piped_content is None and args.pattern is None and not args.interactive:
      kalle.console_stderr.print("[red]Need a request")
      sys.exit(1)

    kwargs = process_args(**vars(args))
    kwargs["piped_content"] = piped_content

    # extract the model params if passed
    from kalle.domain.ModelConfig import ModelParam

    args_model_params = []
    if args.temp is not None:
      args_model_params.append(ModelParam(key="temperature", value=args.temp))
    if args.seed is not None:
      args_model_params.append(ModelParam(key="seed", value=args.seed))
    kwargs["args_model_params"] = args_model_params

    # extract the constrainer if available in the cli args
    constrainer = None
    if args.regex is not None:
      from kalle.domain.Constrainer import Constrainer, ConstrainerType

      constrainer = Constrainer(
          type=ConstrainerType("regex"),
          value=args.regex,
      )

    elif args.jsonschema is not None:
      from kalle.domain.Constrainer import Constrainer, ConstrainerType

      constrainer = Constrainer(
          type=ConstrainerType("jsonschema"),
          value=load_json_schema(kalle, args.jsonschema),
      )
    kwargs["constrainer"] = constrainer

    if not args.interactive:
      asyncio.run(kalle.run(**kwargs))
    else:
      if kwargs["piped_content"] is not None:
        kalle.console_stderr.print("[bold red]Interactive mode can't be used with piped input")
        sys.exit(6)

      from .prompt import CliPrompt

      from kalle.lib.util.ToolHandler import ToolHandler

      tool_handler = ToolHandler(kalle.config, ".")
      all_tools = list(tool_handler.get_tools().keys())
      prompt_history = []
      kalle.conversing = True
      if (
          kalle.config.interactive_style != "plain"
          and kalle.config.format_output
          and kwargs["conversation_key"] is not None
      ):
        kalle.show_history(kwargs["conversation_key"])

      while kalle.conversing:
        if kwargs["param_content"] is not None and kwargs["param_content"] != "":
          asyncio.run(kalle.run(**kwargs))

        prompt = ""
        if kalle.config.interactive_style != "plain" and kalle.config.format_output:
          while prompt == "":
            prompt_input = CliPrompt(
                follow_uris=kwargs["follow_uris"],
                all_tools=all_tools,
                use_tools=kwargs["use_tools"],
                tool_list=kwargs["tool_list"],
                format_output=kwargs["format_output"],
                conversation_key=kwargs["conversation_key"],
                pattern_key=kwargs["args_pattern_key"],
                debug=kwargs["debug"],
            )
            res = prompt_input.run(inline=True, mouse=False)
            if res is None or res == -1:
              sys.exit(0)
            if prompt_input.value is not None:
              prompt = prompt_input.value.strip()
              kwargs["follow_uris"] = prompt_input.follow_uris
              kwargs["format_output"] = prompt_input.format_output
              kwargs["tool_list"] = prompt_input.tool_list
              kwargs["use_tools"] = prompt_input.use_tools
              kwargs["debug"] = prompt_input.kalle_debug
        else:
          prompt = kalle.console.input("[yellow bold]ツ> ")

        kwargs["param_content"] = prompt
        # print(kwargs)
        if kalle.config.interactive_style != "plain" and kalle.config.format_output:
          kalle.console.print(
              Panel(
                  Markdown(f"{prompt}"),
                  subtitle="[white bold]< User >",
                  subtitle_align="right",
                  border_style="blue",
              )
          )

        prompt_history.append(prompt)
  except EOFError:
    sys.exit(0)
  except Exception as e:
    kalle.console_stderr.print(f"[red]An error occurred: {e=}")
    if debug:
      kalle.console_stderr.print_exception()


if __name__ == "__main__":
  cli()
