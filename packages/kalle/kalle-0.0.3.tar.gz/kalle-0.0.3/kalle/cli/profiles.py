from kalle.lib.util.ConfigManager import ConfigManager


def cli():
  config = ConfigManager("kalle", "fe2", ".")

  for p in config.profiles.keys():
    print(f"{p}")
