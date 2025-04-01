# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import datetime
import os
from . import Tool


class UpdateFile(Tool.Tool):

  def __init__(self, config, base_file_dir):
    super().__init__(config)
    self.base_file_dir = base_file_dir

  def key():
    return "update_file"

  def get_prompt(self):
    return f"""Use the function 'update_file' to create, make, change or update a file with requested changes.
    Place the file contents into the following form:
    <body=body_ref_id>contents here</body>

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "update_file",
        "description": "Create, make, change or update the specified file with the new contents",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file, e.g., example/path/to/the/file.txt"
                },
                "body_ref": {
                    "type": "string",
                    "description": "The reference id to the associated body tag."
                },
                "required": ["path", "body_ref"]
            }
        }
    }
}
"""

  def invoke(self, data):
    path = None
    body = None

    if "path" in data:
      path = data["path"]

    if "body" in data:
      body = data["body"]

    if path is not None and path.startswith("/"):
      path = path[1:]

    # Create a backup of the file before updating
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    backup_path = f"{path}.bak_{timestamp}"
    response = ""
    file_change_type = "created"
    try:
      if os.path.exists(f"{self.base_file_dir}/{path}"):
        if os.path.exists(f"{self.base_file_dir}/{backup_path}"):
          return (False, f"Report to the user: Backup file already exists: {backup_path}", "text")
        os.replace(f"{self.base_file_dir}/{path}", f"{self.base_file_dir}/{backup_path}")
        file_change_type = "updated"
        response += f"Report to the user: Existing file backed up as '{backup_path}'\n"
      dir_path = os.path.dirname(path)  # type: ignore
      if not os.path.exists(f"{self.base_file_dir}/{dir_path}"):
        os.makedirs(f"{self.base_file_dir}/{dir_path}")

      with open(f"{self.base_file_dir}/{path}", "w") as f:
        f.write(body or "")
        response += f"Report to the user: File '{path}' {file_change_type}\n"
        self.console_stderr.print(f"[red]{file_change_type.upper()}: {path}\n")
        return (True, response, "text")
    except Exception as e:
      if self.config.debug:
        self.console_stderr.print_exception(show_locals=True)
      return (False, f"Report to the user: An error occurred while writing to '{path}': {e}\n", "text")
