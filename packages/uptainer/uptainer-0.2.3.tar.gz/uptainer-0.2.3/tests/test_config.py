import structlog
from uptainer.loader import Loader
from uptainer.config import Config
from pathlib import Path

log = structlog.get_logger()


def test_config():
    loader_obj = Loader(log=log, config_file=Path("tests/assets/config.yaml"))
    config = loader_obj.read_config()["data"]["repos"][0]
    config_obj = Config()
    config_obj.load(config=config)
    assert config_obj.name == "Foo"
