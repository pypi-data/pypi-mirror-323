from typing import Any
from os import environ


class Config:
    def __init__(self) -> None:
        """Configuration class for the uptainer Object.

        Args:
            None

        Returns:
            None
        """
        self.name = None
        self.image_repository = None
        self.git_ssh_url = None
        self.git_ssh_privatekey = None
        self.git_values_filename = None
        self.values_key = None
        self.version_match = None
        self.git_branch = None

    def load(self, config: dict[Any, Any]) -> None:
        """Load the config given from the file and inject it into the class vars.

        Args:
            config (dict): The config dict given from uptainer.loader.Loader.read_config

        Returns:
            None
        """
        mandatory_vars = [
            "name",
            "image_repository",
            "git_ssh_url",
            "git_values_filename",
            "values_key",
            "version_match",
        ]

        for itervar in mandatory_vars:
            if config[itervar]:
                setattr(self, itervar, config[itervar])

        if "git_branch" in config:
            self.git_branch = config["git_branch"]
        else:
            self.git_branch = "main"

        if "git_ssh_privatekey" in config:
            self.git_ssh_privatekey = config["git_ssh_privatekey"]
        else:
            homedir = environ.get("HOME", "/tmp")
            self.git_ssh_privatekey = f"{homedir}/.ssh/id_rsa"
