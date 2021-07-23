from dataclasses import dataclass
from abc import abstractmethod


@dataclass
class BaseRequest:
    path: str
    body: (dict, bytes)
    method: str
    headers: dict
    query: dict

    def __init__(self, raw):
        self._raw = raw

    @property
    @abstractmethod
    def authorizer(self) -> dict:
        return self._raw.get("requestContext", {}).get("authorizer")
