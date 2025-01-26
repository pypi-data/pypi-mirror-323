"""Main module."""

from structlog._config import BoundLoggerLazyProxy
from structlog.contextvars import bind_contextvars
from box import Box
from os.path import exists
from urllib.parse import urlparse
from uptainer.config import Config
from uptainer.providers.github import GitHub
from uptainer.providers.dockerhub import DockerHub
from uptainer.providers.baseprovider import BaseProvider
from uptainer.git import Git
from uptainer.typer import TyperImageProvider, TyperDetectedVersion, TyperImageList, TyperGenericReturn
import re
import yaml


class UpTainer:
    def __init__(self, config: Config, log: BoundLoggerLazyProxy) -> None:
        """Main class of the package.

        Args:
            config (Config): Uptainer Config class, it will contain all the infos.
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog

        Returns:
            None
        """
        self.config = config
        self.log = log
        bind_contextvars(reponame=self.config.name)
        self.provider = BaseProvider(log=self.log)
        self.image_provider = None
        self.yamlcontent = None

    def get_image_provider(self, image_repository: str) -> TyperImageProvider:
        """Return container image provider.

        Args:
            image_repository (str): Container Image repository url

        Returns:
            Return a dict that have image provider object.
            Its like: {"error": <bool>, "data": "<provider object>"}
        """
        out = TyperImageProvider(error=False, data=BaseProvider(log=self.log))
        DOCKERHUB_SPLITSLASHES = 2
        image_repository = image_repository.replace("https://", "").replace("http://", "")

        if image_repository:
            urlparsed = urlparse(f"//{image_repository}")
            if urlparsed.netloc == "ghcr.io":
                out["data"] = GitHub(log=self.log)
            if urlparsed.netloc == "docker.io":
                out["data"] = DockerHub(log=self.log)
            if len(image_repository.split("/")) <= DOCKERHUB_SPLITSLASHES:
                # Match Dockerhub default format when the hostname its not specified.
                out["data"] = DockerHub(log=self.log)
        else:
            out["error"] = True
        return out

    def detect_version(self, tags: list[TyperImageList]) -> TyperDetectedVersion:
        """Find the latest version to apply.

        Args:
            tags (list): The list of the tags found from the remote repo.

        Returns:
            Return a dict that have version matched.
            Its like: {"error": <bool>, "data": "<matched version>"}
        """
        matched = False
        out = TyperDetectedVersion(error=False, data=None)
        self.log.debug(f"Regex to match: {self.config.version_match}")
        for tagiter in tags:
            if matched:
                break
            for tag in tagiter["name"]:
                version = re.match(self.config.version_match, tag)
                if version:
                    matched = True
                    out["data"] = version.string
                    break
        if not matched:
            out["error"] = True
            self.log.error("Error during detecting version.")
        return out

    def detect_current_version(self, fpath: str, key: str) -> TyperDetectedVersion:
        """Reading and return the tag image used on the git project.

        Args:
            fpath (str): Absolute path of the yaml file to read.
            key (str): Key path to read on the yaml, like "image.tag".

        Returns:
            TyperDetectedVersion object
        """
        out = TyperDetectedVersion(error=False, data=None)
        if exists(fpath):
            box = Box.from_yaml(filename=fpath, Loader=yaml.FullLoader, default_box=True, box_dots=True)
            out["data"] = box[key]
        else:
            self.log.error(f"File '{fpath}' not exists")
            out["error"] = True
        return out

    def update_version(self, fpath: str, key: str, newversion: str) -> TyperGenericReturn:
        """Update the tag image used on the git project in the values file specified.

        Args:
            fpath (str): Absolute path of the yaml file to read.
            key (str): Key path to read on the yaml, like "image.tag".
            newversion (str): New version to apply.

        Returns:
            TyperDetectedVersion object
        """
        out = TyperGenericReturn(error=False, data=None)
        if exists(fpath):
            box = Box.from_yaml(filename=fpath, Loader=yaml.FullLoader, default_box=True, box_dots=True)
            box[key] = newversion
            fopen = open(fpath, "w")
            fopen.write(box.to_yaml())
            fopen.close()
            self.log.info(f"Pushing the key '{key}' into '{fpath}'")
        else:
            self.log.error(f"File '{fpath}' not exists")
            out["error"] = True
        return out

    def run(self) -> None:
        """Main function to check repos.

        Args:
            None

        Returns:
            None
        """
        self.log.info(f"Running check named: '{self.config.name}'")
        image_provider = self.get_image_provider(image_repository=self.config.image_repository)
        if not image_provider["error"]:
            self.provider = image_provider["data"]
        else:
            self.log.error("Image provider detecting fail, please check it.")
            return
        self.log.info(f"Image provider detected: '{self.provider}'")
        self.log.info("Getting the image tags from the provider")
        metadata = self.provider.get_metadata(image_repository=self.config.image_repository)
        if metadata["error"]:
            self.log.error("Error during getting the tags.")
            return

        tags = self.provider.get_image_versions(metadata["data"]["parent"], metadata["data"]["project"])
        if tags["error"]:
            self.log.error("Error getting the tags")
            return

        version = self.detect_version(tags=tags["data"])
        if version["error"]:
            self.log.error("Error during matching the version.")
            return

        self.log.info(f"The version to apply: {version['data']}")
        git_obj = Git(
            log=self.log,
            remote_url=self.config.git_ssh_url,
            branch=self.config.git_branch,
            ssh_private_key=self.config.git_ssh_privatekey,
        )
        git_obj.create_workdir()
        pull_check = git_obj.clone_repo()
        if pull_check["error"]:
            return
        current_version = self.detect_current_version(
            fpath=f"{git_obj.work_directory}/{self.config.git_values_filename}", key=self.config.values_key
        )
        if current_version["error"]:
            return
        self.log.info(f"Version detected Current: {current_version['data']} / To apply: {version['data']}")
        self.update_version(
            fpath=f"{git_obj.work_directory}/{self.config.git_values_filename}",
            key=self.config.values_key,
            newversion=version["data"],
        )
        git_obj.push_repo(fpath=self.config.git_values_filename, newversion=version["data"])
        self.log.info("---> Done.")
