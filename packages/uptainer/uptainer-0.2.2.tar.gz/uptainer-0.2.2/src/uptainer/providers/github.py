from os import getenv
from structlog._config import BoundLoggerLazyProxy
from datetime import datetime
from uptainer.typer import TyperImageVersion, TyperMetadata
from .baseprovider import BaseProvider
import requests


class GitHub(BaseProvider):
    def __init__(self, log: BoundLoggerLazyProxy) -> None:
        """GitHub provider for getting the information from it.

        Args:
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog

        Returns:
            None
        """
        self.endpoint = "https://api.github.com"
        self.name = "GitHub"
        self.max_pages = 20
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        auth_token = getenv("GITHUB_API_TOKEN", default=None)
        self.log = log
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        else:
            self.log.error("Github Token needed for getting the information from Github.")
            return

    def get_image_versions(self, parent: str, project: str) -> TyperImageVersion:
        """Query the Github API in order to get the images version availables and return a list of it.

        Args:
            parent (str): User or Orgs on Github
            project (str): Project Name on GitHub

        Returns:
            Return a dict that have image metadata like:
            {"error": <bool>, "data": [{"last_update": "<datetime object>", "name": ['<version1>', ...]},]}
        """
        STATUS_CODE_OK = 200
        out = TyperImageVersion({"error": False, "data": []})
        endpoint = f"{self.endpoint}/users/{parent}/packages/container/{project}/versions"
        self.log.info(f"Getting image versions from GitHub for the User/Orgs: '{parent}' and project: '{project}'")
        req = requests.get(endpoint, headers=self.headers)
        tmpdb = []
        if req.status_code == STATUS_CODE_OK:
            self.log.debug(f"Returned Status code {STATUS_CODE_OK}")
            for item in req.json():
                if item["metadata"]["container"]["tags"]:
                    tmpdb.append(item)
            if "Link" in req.headers:
                self.log.info("The response contains a pagination, starting iteration over it.")
                for page in range(0, self.max_pages - 1):
                    iter_endpoint = req.headers["Link"].split("<")[1].split(">")[0]
                    self.log.debug(f"Getting {iter_endpoint}")
                    req = requests.get(iter_endpoint, headers=self.headers)
                    for item in req.json():
                        if item["metadata"]["container"]["tags"]:
                            tmpdb.append(item)
                    if "Link" not in req.headers:
                        break
            for item in tmpdb:
                itemdate = datetime.strptime(item["updated_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                out["data"].append({"last_update": itemdate, "name": item["metadata"]["container"]["tags"]})
        else:
            self.log.error(f"Error during getting image, returns: {req.json()}")
            out["error"] = True
        return out

    def get_metadata(self, image_repository: str) -> TyperMetadata:
        """Getting the GitHub metadata like user and orgs.

        Args:
            image_repository (str): Url on ghcr in order to detect the needed data.

        Returns:
            Return a dict that have image metadata like:
            {"error": <bool>, "data": {"parent": "<organization name or user>", "project": "<project name>"}}
        """
        out = TyperMetadata({"error": False, "data": {"parent": "", "project": ""}})
        self.log.info("Getting Metadata from 'GitHub'")
        if image_repository.startswith("ghcr"):
            ir_split = image_repository.split("/")
            out["data"]["parent"] = ir_split[1]
            out["data"]["project"] = ir_split[2]
        else:
            self.log.error("The image repository not start with ghcr.")
            out["error"] = True
        return out
