# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from . import Tool


class ErrorTestTool(Tool.Tool):

  def __init__(self, config, base_file_dir):
    super().__init__(config)
    self.base_file_dir = base_file_dir

  def key():
    return "error_test_tool"

  def get_prompt(self):
    return f"""DO NOT USE THIS TOOL FOR TESTING ONLY:

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "error_test_tool"<
        "description": "DO NOT USE THIS TOOL FOR TESTING ONLY",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "COMPLETELY IRRELEVANT TEXT"
                },
                "required": ["text"]
            }
        }
    }
}
"""

  def invoke(self, data):
    text = data["text"] if "text" in data else None

    return False, text, "text"
