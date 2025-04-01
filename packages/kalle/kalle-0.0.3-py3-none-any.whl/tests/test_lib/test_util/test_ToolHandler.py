# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ToolHandler import ToolHandler
from tempfile import TemporaryDirectory
from kalle.lib.tools.Tool import Tool


class TestToolHandler(unittest.TestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.config = ConfigManager(
        appname, appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=False, debug=True
    )
    self.temp_dir = TemporaryDirectory()
    self.tool_handler = ToolHandler(self.config, base_file_dir=self.temp_dir.name, tool_list=[])

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_get_tools(self):
    tools = self.tool_handler.get_tools()
    self.assertIsInstance(tools, dict)
    for _, tool in tools.items():
      self.assertIsInstance(tool, Tool)

  def test_init(self):
    self.assertIsNotNone(self.tool_handler)

  def test_invoke_tool(self):
    result = self.tool_handler.invoke_tool(
        "update_file",
        {
            "path": "test_invoke.txt",
            "body": "Hello, World! (invoke)",
        },
    )
    self.assertIsNotNone(result)
    with open(os.path.join(self.temp_dir.name, "test_invoke.txt"), "r") as f:
      self.assertEqual(f.read(), "Hello, World! (invoke)")

  def test_invoke_tool_error(self):
    with self.assertRaises(Exception):
      self.tool_handler.invoke_tool(
          "error_test_tool",
          {
              "text": "text",
          },
      )

  def test_invoke_tool_invalid(self):
    with self.assertRaises(Exception):
      self.tool_handler.invoke_tool(
          "invalid_tool",
          {
              "path": "test.txt",
              "contents": "Hello, World!",
          },
      )

  def test_process(self):
    text = '<function=update_file>{"path": "test_process.txt", "body_ref": "hello_world_ref"}</function>\n<body=hello_world_ref>Hello, World! (process)</body>\n'
    result = self.tool_handler.process(text)
    self.assertIsNotNone(result)
    with open(os.path.join(self.temp_dir.name, "test_process.txt"), "r") as f:
      self.assertEqual(f.read(), "Hello, World! (process)")

  def test_process_invalid(self):
    text = 'tool://{"name": "invalid_tool", "parameters": {"path": "test_process.txt", "contents": "Hello, World! (process)"}}\n'
    text = '<function=invalid_tool>{"arg1": "something"}</function>\n'
    message = self.tool_handler.process(text)
    self.assertEqual(
        message,
        "Report to the user that there was an internal issue invoking a tool (invalid_tool Unsupported Tool: invalid_tool) and ask the user to try again. Don't make any promises.\n",
    )

  def test_register_tool(self):
    self.tool_handler.register_tool("test_tool", Tool(self.config))
    tools = self.tool_handler.get_tools()
    self.assertIn("test_tool", tools)
