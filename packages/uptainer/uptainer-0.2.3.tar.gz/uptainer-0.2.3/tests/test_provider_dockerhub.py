import structlog
from uptainer.providers.dockerhub import DockerHub

log = structlog.get_logger()


def test_metadata():
    provider_dh = DockerHub(log=log)
    metadata = provider_dh.get_metadata("mirio/githubapi-proxycache")
    assert metadata["data"]["project"] == "githubapi-proxycache"

    metadata = provider_dh.get_metadata("docker.io/mirio/githubapi-proxycache")
    assert metadata["data"]["project"] == "githubapi-proxycache"

    metadata = provider_dh.get_metadata("redis")
    assert metadata["data"]["parent"] == "library"

def test_image_version():
    provider_dh = DockerHub(log=log)
    image_versions = provider_dh.get_image_versions("library", "nginx")
    assert len(image_versions["data"]) == 200

    image_versions = provider_dh.get_image_versions("mirio", "githubapi-proxycache")
    assert image_versions["data"][0]["name"] == ["latest"]
