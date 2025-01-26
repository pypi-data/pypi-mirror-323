from typing import TypedDict, Any
from re import Match
from datetime import datetime


class TyperConfig(TypedDict):
    repos: list[dict[Any, Any]]


class TyperConfigs(TypedDict):
    error: bool
    data: TyperConfig


class TyperImageList(TypedDict):
    name: str
    last_update: datetime


class TyperMetadataDict(TypedDict):
    parent: str
    project: str


class TyperImageVersion(TypedDict):
    error: bool
    data: list[TyperImageList]


class TyperMetadata(TypedDict):
    error: bool
    data: TyperMetadataDict


class TyperImageProvider(TypedDict):
    error: bool
    data: object


class TyperDetectedVersion(TypedDict):
    error: bool
    data: Match[str] | None


class TyperGenericReturn(TypedDict):
    error: bool
