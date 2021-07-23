from restless.util import camel_to_snake, snake_to_camel, UniversalEncoder
from restless.interfaces import BaseRequest
import json
from urllib.parse import unquote_plus
from base64 import b64decode, b64encode
from typing import Iterable


class Request(BaseRequest):
    @property
    def authorizer(self) -> dict:
        return self._raw.get("requestContext", {}).get("authorizer")

    def __init__(self, raw, use_camel_case=True):
        super().__init__(raw)
        self.path = unquote_plus(raw.get("path") or raw.get("rawPath"))

        if raw.get('isBase64Encoded'):
            self.body = b64decode(raw["body"].encode()) if raw.get("body") else None
        else:
            self.body = json.loads(raw["body"]) if raw.get("body") else None

        self.method = raw.get("httpMethod") or raw.get('requestContext', {}).get("http", {}).get("method")
        self.headers = raw.get("headers", {})
        self.query = raw.get("queryStringParameters") or {}

        if use_camel_case:
            for member in ['body', 'headers', 'query']:
                setattr(self, member, camel_to_snake(getattr(self, member)))


class Response(dict):
    def __init__(self, body="", status_code=200, headers=None, use_camel_case=True):
        super().__init__(
            statusCode=status_code,
            headers=headers or {}
        )

        if isinstance(body, bytes):
            self["isBase64Encoded"] = True
            self["body"] = b64encode(body).decode()
        elif isinstance(body, (dict, Iterable)):
            self["isBase64Encoded"] = False

            if isinstance(body, str):
                self["body"] = body
            else:
                if "Content-Type" not in self["headers"]:
                    self["headers"]["Content-Type"] = "application/json"

                if use_camel_case:
                    body_ = snake_to_camel(body)
                else:
                    body_ = body

                self["body"] = json.dumps(body_, cls=UniversalEncoder)
        else:
            raise Exception("Unsupported")
