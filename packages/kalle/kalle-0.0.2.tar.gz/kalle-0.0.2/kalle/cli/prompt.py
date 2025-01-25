# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import TextArea, Label, Button
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
    line_count = min(len(self.text.split("\n")), self.max_height)
    self.app.screen.styles.height = line_count + 2


class Prompt(App):
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
    color: dodgerblue;
    background: dodgerblue;
    margin-left: 1;
    padding: 0;
    text-style: bold;
    tint: white 10%;
    width: 3;
}

#options {
    border: round dodgerblue;
    padding-left: 1;
    padding-right: 1;
    display: none;
}

#button-group {
    /* width: 21; */
    width: 18;
}

"""

  def __init__(self) -> None:
    self.value = None
    super().__init__()

  def compose(self) -> ComposeResult:
    self.prompt_line = Horizontal(id="prompt-line")
    with self.prompt_line:
      with Horizontal(id="prompt"):
        yield Label("ツ> ", id="prompt-label")
        self.input = InputTextArea(id="input", show_line_numbers=False, soft_wrap=True)
        yield self.input
      with Vertical(id="button-group"):
        with Horizontal():
          yield Button("Send", id="input-button")
      #    yield RadioButton("", id="options-enable")
      #  with Vertical(id="options"):
      #    yield Label("ONE")
      self.input.focus()

  def submit(self) -> None:
    self.value = self.input.text
    self.app.exit(0)

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "input-button":
      self.submit()

  def on_key(self, event: Key) -> None:
    if event.key in ["ctrl+c", "ctrl+d", "ctrl+q"]:
      self.app.exit(-1)


if __name__ == "__main__":

  conversation_key = "default"
  prompt = ""
  app = Prompt()
  app.run(inline=True)

  print(f"TEXT:\n{prompt}")
