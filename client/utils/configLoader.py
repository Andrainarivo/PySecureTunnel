import os
import yaml
from pathlib import Path


class ConfigLoader:
    """
    Chargeur de configuration basé sur un fichier YAML.

    Attributes:
        yaml_path (Path): Chemin du fichier YAML.
        config (dict): Configuration chargée.
    """

    def __init__(self, yaml_path: Path = None):
        self.yaml_path = yaml_path
        self.config = {}

    def load(self) -> dict:
        """Charge le fichier YAML dans self.config et retourne le dict final."""

        # Charger YAML
        if self.yaml_path:
            with open(self.yaml_path, "r") as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    self.config.update(yaml_config)

        return self.config
