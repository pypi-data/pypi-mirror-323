import structlog
from datetime import datetime
from uptainer.loader import Loader
from uptainer.config import Config
from uptainer.uptainer import UpTainer
from pathlib import Path

log = structlog.get_logger()


def test_imageprovider():
    loader_obj = Loader(log=log, config_file=Path("tests/assets/config.yaml"))
    config = loader_obj.read_config()["data"]["repos"][0]
    config_obj = Config()
    config_obj.load(config=config)
    obj = UpTainer(config=config_obj, log=log)

    provider = obj.get_image_provider(
        image_repository=config_obj.image_repository
    )
    assert str(provider["data"]) == "GitHub"

    providerdockerhub = obj.get_image_provider(image_repository="docker.io/redis")
    assert str(providerdockerhub["data"]) == "DockerHub"

    providermissing = obj.get_image_provider(
        image_repository="example.com/provider/missing"
    )
    assert str(providermissing["data"]) == "Base"

    providernoimage = obj.get_image_provider(image_repository="")
    assert providernoimage["error"] == True

def test_detect_version():
    loader_obj = Loader(log=log, config_file=Path("tests/assets/config.yaml"))
    config = loader_obj.read_config()["data"]["repos"][0]
    config_obj = Config()
    config_obj.load(config=config)
    obj = UpTainer(config=config_obj, log=log)

    detecterror = obj.detect_version(tags=[
        {'last_update': datetime(2024, 11, 16, 19, 58, 7), 'name': ['pr-13939']}
    ])
    assert detecterror["error"] == True

    matched = obj.detect_version(tags=[
        {'last_update': datetime(2024, 11, 16, 19, 58, 7), 'name': ['v1.0.1']}
    ])
    assert matched["data"] == "v1.0.1"
