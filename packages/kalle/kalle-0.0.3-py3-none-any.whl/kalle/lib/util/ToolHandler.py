# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys
import re
import json
import importlib
import inspect

from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax

from kalle.lib.tools.Tool import Tool


class ToolHandler:

  def __init__(self, config, /, base_file_dir: str, tool_list: list[str] | None = None, console_stderr: Console = None):
    self.config = config
    self.base_file_dir = base_file_dir
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    if tool_list == []:
      tool_list = None
    self.tool_list = tool_list
    self.tools = {}

    tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
    for file_name in os.listdir(tools_dir):
      if file_name.endswith(".py") and not file_name.startswith("__"):
        module_name = file_name[:-3]
        module = importlib.import_module(f"kalle.lib.tools.{module_name}")
        for name, obj in inspect.getmembers(module):
          if inspect.isclass(obj) and issubclass(obj, Tool) and obj is not Tool:
            if tool_list is None or (tool_list is not None and obj.key() in tool_list):
              self.register_tool(obj.key(), obj(self.config, self.base_file_dir))

  # register the tool for use
  def register_tool(self, tool_name: str, tool):
    self.tools[tool_name] = tool

  # return a list of tools
  def get_tools(self):
    return self.tools

  # invoke the tool
  def invoke_tool(self, tool_name, data):
    if self.config.debug:
      self.console_stderr.print(Panel(f"[magenta]{tool_name}", title="[bold magenta]INVOKING TOOL", style="magenta"))
    if tool_name in self.tools:
      success, resp, syntax = self.tools[tool_name].invoke(data)
      if success:
        return resp, syntax
      raise Exception(f"Could not invoke tool: {tool_name} ({resp})")
    else:
      raise ValueError(f"Unsupported Tool: {tool_name}")

  def extract_function_contents(self, text):
    pattern = r"<function=([^>]+)>(.*?)</function>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

  def extract_body_contents(self, text):
    pattern = r"<body=([^>]+)>(.*?)</body>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

  def process(self, text):
    if self.config.debug:
      self.console_stderr.rule("[bold magenta]Processing initial LLM response for tool calls", style="magenta")

    bodies = self.extract_body_contents(text)
    functions = self.extract_function_contents(text)

    body = {}
    for b in bodies:
      body[b[0]] = b[1]

    resp = ""
    function_responses = []
    for f in functions:
      func_name = f[0]
      params_string = re.sub(r"\\'", "'", f[1])
      params = json.loads(params_string)

      if "body_ref" in params and params["body_ref"] in body:
        params["body"] = body[params["body_ref"]]

      try:
        r, syntax = self.invoke_tool(func_name, params)
        function_responses.append({"name": func_name, "response": r, "syntax": syntax})
        resp += f"---\nTOOL_CALL_RESULT({func_name}): {r}\n"
      except Exception as e:
        if self.config.debug:
          self.console_stderr.print("[red]EXCEPTION")
          self.console_stderr.print("[red]  ERROR: ", type(e).__name__, e)
          self.console_stderr.print_exception(show_locals=True)
        resp += f"Report to the user that there was an internal issue invoking a tool ({func_name} {e}) and ask the user to try again. Don't make any promises.\n"

    if self.config.debug:
      self.console_stderr.rule(style="magenta")
      formatted_function_responses = []
      for r in function_responses:
        formatted_function_responses.append(
            Panel(
                Group("[bold magenta]Result:[/bold magenta]", Syntax(str(r["response"]), r["syntax"])),
                title=f"[bold]{r['name']}",
            )
        )

      self.console_stderr.print(
          Panel(Group(*formatted_function_responses), title="[bold magenta]PROCESSING RESPONSE", style="magenta")
      )

      self.console_stderr.print()

    return resp
