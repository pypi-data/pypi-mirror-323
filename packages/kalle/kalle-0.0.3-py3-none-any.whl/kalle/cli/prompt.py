# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from __future__ import annotations

from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import TextArea, Label, Button, Checkbox, Rule
from textual.color import Color
from textual.events import Key


class InputTextArea(TextArea):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.max_height = 10

  def on_key(self, event: Key) -> None:

    match str(event.key):
      case "enter":
        line_count = min(len(self.app.input.text.split("\n")) or 1, self.max_height)
        if line_count == 1:
          self.app.submit()
      case "shift+enter":
        event.prevent_default()
        self.app.input.insert("\n")
      case "ctrl+enter":
        event.prevent_default()
        self.app.submit()

  def on_text_area_changed(self, event) -> None:
    self.app.line_count = len(self.text.split("\n"))
    self.app.update_screen_height()


class CliPrompt(App):
  CSS = """
Screen {
    border: none;
    padding: 0;
    margin: 0;
    height: 3;
    color: red;
}

#prompt-line {
    border: round dodgerblue;
    padding-left: 1;
    padding-right: 1;
    border-title-align: center;
    border-title-color: yellow;
    border-subtitle-align: center;
}

#prompt-label {
    text-style: bold;
    color: yellow;
}

#input {
    width: 100%;
    border: none;
    padding-left: 0;
}

#input-button {
    border: none;
    margin-left: 1;
    padding: 0;
    background: dodgerblue;
}

#options-enable {
    border: none;
    margin-left: 1;
    padding: 0;
    background: dodgerblue;
    min-width: 5;
    /* tint: white 10%; */
    /* width: 3; */
}

#options {
    border: none; /* round dodgerblue; */
    padding-left: 1;
    padding-right: 1;
    display: none;
}

Checkbox {
    border: none;
    padding: 0;
    margin: 0;
    color: dodgerblue;
}

#button-group {
    width: 23;
}

#button-subgroup {
    height: 1;
    margin-bottom: 1;
}

Rule {
  border: none;
  padding: 0;
  margin: 0;
}

#tool-options-enable {
    border: none;
    padding: 0;
    margin: 0;
    margin-left: 1;
    background: dodgerblue;
    min-width: 5;
}

#tool-options {
    height: 1;
    border: none;
    padding: 0;
    margin: 0;
}

#tool-options-list {
    display: none;
}
"""

  def __init__(
      self,
      /,
      follow_uris: bool,
      format_output: bool,
      all_tools: list[str],
      use_tools: bool,
      tool_list: Optional[list[str]] = None,
      conversation_key: Optional[str] = None,
      pattern_key: Optional[str] = None,
      debug: Optional[bool] = False,
  ) -> None:
    self.value = None
    self.follow_uris = follow_uris
    self.tool_list = tool_list
    self.all_tools = all_tools
    self.use_tools = use_tools
    self.format_output = format_output
    self.conversation_key = conversation_key
    self.pattern_key = pattern_key
    self.kalle_debug = debug
    self.options_enable = False
    self.screen_height = {}
    self.line_count = 0
    super().__init__()

  def compose(self) -> ComposeResult:
    self.prompt_line = Horizontal(id="prompt-line")
    if self.conversation_key is not None:
      self.prompt_line.border_title = f"[italic]{self.conversation_key}"
    if self.pattern_key is not None:
      self.prompt_line.border_subtitle = f"[italic]{self.pattern_key}"
    with self.prompt_line:
      with Horizontal(id="prompt"):
        yield Label("ツ> ", id="prompt-label")
        self.input = InputTextArea(id="input", show_line_numbers=False, soft_wrap=True)
        yield self.input
      with Vertical(id="button-group"):
        with Horizontal(id="button-subgroup"):
          yield Button("Send", id="input-button")
          yield Button("O", id="options-enable")
        self.options = Vertical(id="options")
        self.options.styles.display = "none"
        with self.options:
          self.options_follow_uris = Checkbox("Follow URIs", id="options-follow")
          yield self.options_follow_uris
          self.options_use_tools = Checkbox("Tools", id="options-tool")
          with Horizontal(id="tool-options"):
            yield self.options_use_tools
            yield Button("T", id="tool-options-enable")
          self.options_format_output = Checkbox("Format Output", id="options-format")
          yield self.options_format_output
          self.options_debug = Checkbox("Debug", id="options-debug")
          yield self.options_debug

          yield Rule()
          with Vertical(id="tool-options-list"):
            yield Label("[bold yellow]Tools")
            for key in self.all_tools:
              checked = False
              if self.tool_list is not None and key in self.tool_list:
                checked = True
              yield Checkbox(str(key), checked, id=f"options-tool-{key}")

      self.input.focus()
      self.options_follow_uris.value = self.follow_uris or False
      self.options_use_tools.value = self.use_tools
      self.options_format_output.value = self.format_output or False
      self.options_debug.value = self.kalle_debug or False

  def submit(self) -> None:
    self.value = self.input.text
    self.follow_uris = self.query_one("#options-follow", Checkbox).value
    self.use_tools = self.query_one("#options-tool", Checkbox).value
    tool_list = []
    for key in self.all_tools:
      if self.query_one(f"#options-tool-{key}", Checkbox).value:
        tool_list.append(key)
    self.tool_list = tool_list
    self.format_output = self.query_one("#options-format", Checkbox).value
    self.kalle_debug = self.query_one("#options-debug", Checkbox).value
    self.app.exit(0)

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "input-button":
      self.submit()
    if event.button.id == "options-enable":
      self.toggle_options()
    if event.button.id == "tool-options-enable":
      self.toggle_tool_options()

  def update_screen_height(self):
    min_height = 3  # base height
    self.app.screen.styles.height = max(
        min_height, self.line_count + 2, self.screen_height.get("options", 0) + self.screen_height.get("tools_list", 0)
    )

  def toggle_options(self):
    options_button = self.query_one("#options-enable")
    if self.options_enable:
      self.screen_height["options"] = 0
      self.options.styles.display = "none"
      options_button.styles.color = ""
    else:
      self.screen_height["options"] = 8
      self.options.styles.display = "block"
      options_button.styles.color = "orange"
    self.options_enable = not self.options_enable
    self.update_screen_height()

  def toggle_tool_options(self):
    options_button = self.query_one("#tool-options-enable")
    tool_options = self.query_one("#tool-options-list")
    if options_button.styles.color == Color.parse("orange"):
      options_button.styles.color = ""
      self.screen_height["tools_list"] = 0
      # self.app.screen.styles.height = max(line_count + 2, 8)
      tool_options.styles.display = "none"
    else:
      # self.app.screen.styles.height = max(line_count + 2, 25)
      self.screen_height["tools_list"] = 4 + len(self.all_tools or [])
      options_button.styles.color = "orange"
      tool_options.styles.display = "block"
    self.update_screen_height()

  def on_key(self, event: Key) -> None:
    if event.key in ["ctrl+o"]:
      self.toggle_options()
    if event.key in ["ctrl+c", "ctrl+d", "ctrl+q"]:
      self.app.exit(-1)


if __name__ == "__main__":

  conversation_key = "default"
  prompt = ""
  app = CliPrompt()
  app.run(inline=True)

  print(f"TEXT:\n{prompt}")
