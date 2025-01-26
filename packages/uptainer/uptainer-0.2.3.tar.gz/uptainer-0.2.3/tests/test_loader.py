import structlog
from uptainer.loader import Loader
from pathlib import Path

log = structlog.get_logger()


def test_loader_noexists():
    loader_obj_missing = Loader(log=log, config_file=Path("/tmp/noexist"))
    config = loader_obj_missing.read_config()
    assert config["error"] == True
    loader_obj_missing.run()


def test_loader():
    loader_obj = Loader(log=log, config_file=Path("tests/assets/config.yaml"))
    config = loader_obj.read_config()
    assert config["data"]["repos"][0]["name"] == "Foo"
