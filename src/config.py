"""
Configuration module for the Performance Suite.

This module provides functionality to load and access configuration settings
from the config.yaml file.
"""

import os
import yaml
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the Performance Suite."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file. If None, uses the default path.
        """
        if config_path is None:
            # Use the default config path relative to the project root
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml"
            )
        else:
            self.config_path = config_path

        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from the YAML file."""
        try:
            with open(self.config_path, "r") as config_file:
                self.config_data = yaml.safe_load(config_file)
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_path}")
            self.config_data = {}
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            self.config_data = {}

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            section: The configuration section.
            key: The specific key within the section. If None, returns the entire section.
            default: Default value to return if the key is not found.

        Returns:
            The configuration value or default if not found.
        """
        if section not in self.config_data:
            return default

        if key is None:
            return self.config_data[section]

        return self.config_data[section].get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            section: The configuration section.
            key: The specific key within the section.
            value: The value to set.
        """
        if section not in self.config_data:
            self.config_data[section] = {}

        self.config_data[section][key] = value

    def save(self) -> None:
        """Save the current configuration to the YAML file."""
        try:
            with open(self.config_path, "w") as config_file:
                yaml.dump(self.config_data, config_file, default_flow_style=False)
        except Exception as e:
            print(f"Error saving configuration file: {e}")


# Global configuration instance
config = Config()
