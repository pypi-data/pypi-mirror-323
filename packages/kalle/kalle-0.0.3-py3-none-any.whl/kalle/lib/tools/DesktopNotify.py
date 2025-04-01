# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from . import Tool
import subprocess
import platform


class DesktopNotify(Tool.Tool):

  def __init__(self, config, base_file_dir):
    super().__init__(config)
    self.base_file_dir = base_file_dir

  def key():
    return "desktop_notify"

  def get_prompt(self):
    return f"""Use the function 'desktop_notify' to send a message to the user's computer.

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "desktop_notify",
        "description": "Send a message to the user's computer.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the message to send."
                },
                "message": {
                    "type": "string",
                    "description": "The message to send."
                },
                "required": ["message"]
            }
        }
    }
}
"""

  def invoke(self, data):
    title = data["title"]
    message = data["message"]

    if platform.system() == "Darwin":  # OSX
      title = title.replace('"', '\\"')
      message = message.replace('"', '\\"')
      result = subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
      if result.returncode != 0:
        return False, f"Report that there was a problem sending the notification: {result.stderr}", "text"
    else:  # Linux
      result = subprocess.run(["notify-send", title, message])
      if result.returncode != 0:
        return False, f"Report that there was a problem sending the notification: {result.stderr}", "text"

    return True, "Report that the notification was sent.", "text"
