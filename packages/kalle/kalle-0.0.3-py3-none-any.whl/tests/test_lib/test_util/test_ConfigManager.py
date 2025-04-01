# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys
import unittest

from unittest.mock import patch

from kalle.lib.util.ConfigManager import ConfigManager, find_conversation_key

from kalle.domain.Pattern import Pattern
from kalle.domain.Profile import Profile
from kalle.domain.Connector import Connector
from kalle.domain.PromptTemplate import PromptTemplate
from kalle.domain.Constrainer import Constrainer, ConstrainerType


class TestConfigManager(unittest.TestCase):

  def setUp(self):
    self.appname = "kalle"
    self.appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.maxDiff = 1000

  def tearDown(self):
    try:
      self.config = None
    except AttributeError:
      pass

  # @TODO should the path somehow be capped so it doesn't escape the text fixture?
  def test_find_conversation_key(self):
    # Test when .kalle_conversation file is not found
    conversation_key = find_conversation_key(self.fixtures_dir)
    self.assertIsNone(conversation_key)

    # Test when .kalle_conversation file is not found in any parent directories
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.1/testdir1.1.1/"))
    self.assertIsNone(conversation_key)

    # Test when .kalle_conversation file is found in the specifed directory
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.2/"))
    self.assertEqual(conversation_key, "testconversation1.2.2")

    # Test when .kalle_conversation file is found in a parent directory
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1/"))
    self.assertEqual(conversation_key, "testconversation1.2")

  def test_config_init(self):
    # Test basic init
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=False
    )
    self.assertIsNotNone(self.config)

    # Test that default is the conversation key
    self.assertEqual(type(self.config), ConfigManager)
    self.assertEqual(os.path.relpath(self.config.config_dir), "tests/fixtures")  # type: ignore
    self.assertEqual(self.config.cache_dir, "tests/fixtures/kalle_cache")
    self.assertEqual(self.config.data_dir, "tests/fixtures/kalle_data")
    self.assertEqual(self.config.format_output, False)
    self.assertEqual(self.config.google_app_credentials_path, "tests/fixtures/fake_creds.json")
    self.assertEqual(self.config.interactive_style, "plain")

  # test the happy path of a good yaml with correct keys
  def test_config_validate_good(self):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key=None, base_file_dir=self.fixtures_dir, use_memory=True
    )

  # test broken yaml
  @patch("sys.exit")
  def test_config_validate_broken(self, mock_exit):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_broken.yml")
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_memory=True,
        debug=True,
    )
    mock_exit.assert_called_once_with(112)

  # Test for invalid keys but well structured yaml
  @patch("sys.exit")
  def test_config_validate_invalid(self, mock_exit):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_invalid.yml")
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_memory=True,
        debug=True,
    )
    mock_exit.assert_called_once_with(110)

  def test_config_validate_missing(self):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_missing.yml")
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_memory=True,
        debug=True,
    )
    self.assertTrue(os.path.exists(os.environ["KALLE_CONFIG"]))

  def test_config_conversation_key_no_conversation_key(self):
    # Test the base case of no passed key and memory (conversation) is in use
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_memory=True,
    )

    # Test that default is the conversation key
    self.assertEqual(self.config.conversation_key, None)

  def test_config_conversation_key_no_conversation_key_with_configured_default(self):
    # Test the base case of no passed key and memory (conversation) is in use
    self.config_file = os.path.join(self.fixtures_dir, "config_default_conversation.yml")
    os.environ["KALLE_CONFIG"] = self.config_file

    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key=None, base_file_dir=self.fixtures_dir, use_memory=True
    )

    # Test that default is the conversation key
    self.assertEqual(self.config.conversation_key, "defaulttest")

  def test_config_conversation_key(self):
    # Test when a specific conversation_key is provided
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="someconversation",
        base_file_dir=self.fixtures_dir,
        use_memory=True,
    )
    self.assertEqual(self.config.conversation_key, "someconversation")

  def test_config_conversation_key_no_conversation_key_kalle_conversation(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  and memory is on
    # The .kalle_conversation should override the 'default'
    sys.stderr = open("/dev/null", "w")
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_memory=True,
    )
    self.assertEqual(self.config.conversation_key, "testconversation1.2")

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  and memory is on
    sys.stderr = open("/dev/null", "w")
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_memory=True,
    )
    self.assertEqual(self.config.conversation_key, "testconversation1.2")

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present_nomemory_kalle_conversation_file(
      self,
  ):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  but we're not using memory so conversations are irrelevant
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_memory=False,
    )
    self.assertIsNone(self.config.conversation_key)

  def test_config_conversation_key_conversation_key_present_no_kalle_conversation_nomemory(self):
    # Test when a conversation_key is provided
    #  no .kalle_conversation files in the path
    #  but we're not using memory so conversations are irrelevant
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="irrelevantkey",
        base_file_dir=self.fixtures_dir,
        use_memory=False,
    )
    self.assertIsNone(self.config.conversation_key)

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present_nomemory(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path,
    #  but we're not using memory so conversations are irrelevant
    self.config = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_memory=False,
    )
    self.assertIsNone(self.config.conversation_key)

  def test_config_properties(self):
    # Test data_dir property
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=True
    )

    # Test properties
    # @TODO add a variation of thos test where the config is empty or missing?
    properties_to_test = [
        ("use_memory", True),
        ("conversation_key", "default"),
        ("conversation_dir", "tests/fixtures/kalle_data/conversations"),
    ]

    for prop, value in properties_to_test:
      with self.subTest(prop=prop, value=value):
        self.assertEqual(getattr(self.config, prop), value)

  def test_config_profiles(self):
    # Test data_dir property
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=True
    )

    properties_to_test = [
        ("base", "llama3_1_70b"),
        ("tiny", "mistralnemoinstruct_2407"),
        ("code", "codestral_22b"),
        ("ollama", "llama3.1:latest"),
        ("openai", "gpt-4o"),
        ("anthropic", "claude-3-5-sonnet-20240620"),
        ("groq", "llama3_1_70b"),
    ]
    for profile, value in properties_to_test:
      with self.subTest(profile=profile, value=value):
        self.assertEqual(getattr(self.config, "profiles")[profile].model, value)

    connector_urls_to_test = [
        ("base", "https://api.fe2.dev/basellm/v1/"),
        ("tiny", "https://api.fe2.dev/tinyllm/v1/"),
        ("code", "https://api.fe2.dev/codellm/v1/"),
        ("ollama", "http://localhost:11434/api/generate"),
        ("tabbyapi", "http://localhost:5000/v1/"),
    ]

    for profile, value in connector_urls_to_test:
      with self.subTest(profile=profile, value=value):
        self.assertEqual(getattr(self.config, "profiles")[profile].connector.url, value)

    connector_keys_to_test = [
        ("base", "NOT_A_REAL_KEY"),
        ("tiny", "NOT_A_REAL_KEY"),
        ("code", "NOT_A_REAL_KEY"),
        ("tabbyapi", "NOT_A_REAL_KEY_FROM_FILE"),
        ("openai", "NOT_A_REAL_KEY"),
        ("anthropic", "NOT_A_REAL_KEY"),
        ("groq", "NOT_A_REAL_KEY"),
    ]

    for profile, value in connector_keys_to_test:
      with self.subTest(profile=profile, value=value):
        self.assertEqual(getattr(self.config, "profiles")[profile].connector.key, value)

  def test_config_prompts(self):
    # Test data_dir property
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=True
    )

    properties_to_test = [
        ("kalle_system_prompt", "Your name is Kalle. You are a helpful, confident, and friendly personal assistant."),
        ("base_tool_prompt", "You are a tool calling agent."),
    ]

    for prop, value in properties_to_test:
      with self.subTest(prop=prop, value=value):
        self.assertEqual(getattr(self.config, "prompts")[prop].value, value)

  def test_config_pattern(self):
    # Test data_dir property
    self.config = ConfigManager(
        self.appname, self.appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_memory=True
    )
    self.assertEqual(self.config.data_dir, "tests/fixtures/kalle_data")

    import sys

    print(self.config.patterns_dir, file=sys.stderr)
    self.assertEqual(
        getattr(self.config, "patterns")["test"],
        Pattern(
            key="test",
            name="Test Pattern",
            system_prompt_template=PromptTemplate(
                key="system_prompt_template",
                name=None,
                value="You are a test result provider. Respond exactly as requested.",
            ),
            prompt_template=PromptTemplate(
                key="prompt_template",
                name=None,
                value="Output YES if the following number is 12321: {{ content }}",
            ),
            tools=None,
            constrainer=Constrainer(
                type=ConstrainerType("regex"),
                value="YES|NO",
            ),
            profile=Profile(
                connector=Connector(
                    name="tabbyapi",
                    url="https://api.fe2.dev/basellm/v1/",
                    key="NOT_A_REAL_KEY",
                ),
                key="base",
                name="base",
                model="llama3_1_70b",
                model_params=[],
            ),
        ),
    )


if __name__ == "__main__":
  unittest.main()
