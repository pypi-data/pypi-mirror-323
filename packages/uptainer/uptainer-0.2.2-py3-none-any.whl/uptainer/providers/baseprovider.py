from structlog._config import BoundLoggerLazyProxy
from uptainer.typer import TyperImageVersion, TyperMetadata, TyperMetadataDict


class BaseProvider:
    def __init__(self, log: BoundLoggerLazyProxy) -> None:
        """BaseProvider.

        Args:
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog

        Returns:
            None
        """
        self.name = "Base"

    def __str__(self) -> str:
        """Return a class string name.

        Args:
            None

        Returns:
            Return a name of the class.
        """
        return self.name

    def get_image_versions(self, parent: str, project: str) -> TyperImageVersion:
        """Query the Provider API in order to get the images version availables and return a list of it.

        Args:
            parent (str): Namespace or User in DockerHub
            project (str): Project Name

        Returns:
            Return a dict that have image metadata like:
            {"error": <bool>, "data": [
                {"last_update": "<datetime object>",
                 "name": ['<version1>', ...]},]
            }
        """
        return TyperImageVersion(error=False, data=[])

    def get_metadata(self, image_repository: str) -> TyperMetadata:
        """Getting the Provider metadata like user and orgs.

        Args:
            image_repository (str): Url on provider in order to detect the needed data.

        Returns:
            Return a dict that have image metadata like:
            {"error": <bool>, "data":
                {"parent": "<organization name or user>",
                 "project": "<project name>"}
            }
        """
        return TyperMetadata(error=False, data=TyperMetadataDict(project="aaa", parent="bbb"))
