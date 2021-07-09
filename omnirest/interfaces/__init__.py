from dataclasses import dataclass


@dataclass
class BaseRequest:
    path: str
    body: (dict, bytes)
    method: str
    headers: dict
    query: dict
    authorizer: dict = None
