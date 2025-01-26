from os import getenv
from structlog._config import BoundLoggerLazyProxy
from datetime import datetime
from uptainer.typer import TyperImageVersion, TyperMetadata
from urllib.parse import urlparse
from .baseprovider import BaseProvider
import requests


class DockerHub(BaseProvider):
    def __init__(self, log: BoundLoggerLazyProxy) -> None:
        """DockerHub provider for getting the information from it.

        Args:
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog

        Returns:
            None
        """
        self.endpoint = "https://hub.docker.com"
        self.headers = {}
        self.name = "DockerHub"
        auth_token = getenv("DOCKERHUB_API_TOKEN", default=None)
        self.log = log
        self.max_pages = 20
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        else:
            self.log.warning("DockerHub Token not found. Using anonymous access.")

    def get_image_versions(self, parent: str, project: str) -> TyperImageVersion:
        """Query the DockerHub API in order to get the images version availables and return a list of it.

        Args:
            parent (str): Namespace or User in DockerHub
            project (str): Project Name

        Returns:
            Return a dict that have image metadata like:
            {'error': <bool>, 'data': [{'last_update': '<datetime object>", 'name': ['<version1>', ...]},]}
        """
        STATUS_CODE_OK = 200
        out = TyperImageVersion({"error": False, "data": []})
        endpoint = f"{self.endpoint}/v2/namespaces/{parent}/repositories/{project}/tags"
        self.log.info(f"Getting image versions from DockerHub for the User/Orgs: {parent} and project: {project}")
        # Get Page 1
        req = requests.get(endpoint, headers=self.headers)
        tmpdb = []
        if req.status_code == STATUS_CODE_OK:
            self.log.debug(f"Returned Status code {STATUS_CODE_OK}")
            for item in req.json()["results"]:
                tmpdb.append(item)
            if req.json()["next"] is not None:
                self.log.info("The response contains a pagination, starting iteration over it.")
                for page in range(0, self.max_pages - 1):
                    iter_endpoint = req.json()["next"]
                    self.log.debug(f"Getting {iter_endpoint}")
                    req = requests.get(iter_endpoint, headers=self.headers)
                    for item in req.json()["results"]:
                        tmpdb.append(item)
                    if req.json()["next"] is None:
                        break
            for item in tmpdb:
                itemdate = datetime.strptime(item["last_updated"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                if isinstance(item["name"], str):
                    tags = [item["name"]]
                else:
                    tags = item["name"]
                out["data"].append({"last_update": itemdate, "name": tags})
        else:
            self.log.error(f"Error during getting image, returns: {req.json()}")
            out["error"] = True
        return out

    def get_metadata(self, image_repository: str) -> TyperMetadata:
        """Getting the DockerHub metadata like user and orgs.

        Args:
            image_repository (str): Url on docker.io in order to detect the needed data.

        Returns:
            Return a dict that have image metadata like:
            {"error": <bool>, "data": {"parent": "<organization name or user>", "project": "<project name>"}}
        """
        DOCKERHUB_SPLITSLASHES = 2
        out = TyperMetadata({"error": False, "data": {"parent": "", "project": ""}})
        self.log.info("Getting Metadata from 'DockerHub'")
        urlparsed = urlparse(f"//{image_repository}")
        if urlparsed.netloc == "docker.io":
            name_split = image_repository.split("/")
            out["data"]["parent"] = name_split[1]
            out["data"]["project"] = name_split[2]
        elif len(image_repository.split("/")) == DOCKERHUB_SPLITSLASHES:
            name_split = image_repository.split("/")
            out["data"]["parent"] = name_split[0]
            out["data"]["project"] = name_split[1]
        else:
            out["data"]["parent"] = "library"
            out["data"]["project"] = image_repository

        if out["data"]["parent"] == "_":
            out["data"]["parent"] = "library"

        return out
