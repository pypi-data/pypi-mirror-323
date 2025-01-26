import structlog
from uptainer.providers.github import GitHub

log = structlog.get_logger()


def test_metadata():
    provider_obj = GitHub(log=log)
    metadata = provider_obj.get_metadata("ghcr.io/mirio/verbacap")
    assert metadata["data"]["parent"] == "mirio"

    metadata_error = provider_obj.get_metadata("example.com/mirio/verbacap")
    assert metadata_error["error"] == True

def test_image_version():
    provider_obj = GitHub(log=log)
    image_versions_fail = provider_obj.get_image_versions("Mirio", "noexists")
    assert image_versions_fail["error"] == True

    image_versions = provider_obj.get_image_versions("Mirio", "verbacap")
    assert image_versions["data"][0]["name"][1] == "latest"

    image_version_pages = provider_obj.get_image_versions("immich-app", "immich-server")
    assert len(image_version_pages["data"]) > 50
