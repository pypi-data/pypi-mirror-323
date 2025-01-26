from yaml import safe_load
from pathlib import Path
from structlog._config import BoundLoggerLazyProxy
from uptainer.config import Config
from uptainer.uptainer import UpTainer
from uptainer.typer import TyperConfigs, TyperConfig


class Loader:
    def __init__(self, log: BoundLoggerLazyProxy, config_file: Path) -> None:
        """Loader class to load all the repos from the config and trasform it into uptainer Classes.

        Args:
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog
            config_file (Path): Config path with PATH class.

        Returns:
            None
        """
        self.log = log
        self.config_file = config_file

    def read_config(self) -> TyperConfigs:
        """Load the config in YAML format and wrap it into a self.config_file var.

        Args:
            None

        Returns:
            None
        """
        self.log.debug("Loading config")
        out = TyperConfigs(error=False, data=TyperConfig(repos=[]))
        if not self.config_file.exists():
            self.log.error("File not exists.")
            out["error"] = True
        else:
            out["data"] = TyperConfig(repos=safe_load(self.config_file.open())["repos"])
        return out

    def run(self) -> None:
        """Main method, it will load the config file and create a uptainer class for each of them.

        Args:
            None

        Returns:
            None
        """
        configdata = self.read_config()
        if configdata["error"]:
            return
        for repo in configdata["data"]["repos"]:
            config = Config()
            config.load(config=repo)
            obj = UpTainer(config=config, log=self.log)
            obj.run()
