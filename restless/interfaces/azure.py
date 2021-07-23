import json
from azure.functions import HttpRequest, HttpResponse
from restless.util import snake_to_camel, camel_to_snake, UniversalEncoder
import re
from urllib.parse import unquote_plus
from restless.interfaces import BaseRequest
from typing import Iterable


def to_camel(body: [str, bytes]):
    try:
        return json.dumps(snake_to_camel(json.loads(body)), cls=UniversalEncoder)
    except json.decoder.JSONDecodeError:
        return body


class Request(BaseRequest):
    BASE_PATH_RE = re.compile('https://.*/api')

    @property
    def authorizer(self) -> dict:
        return self._raw.params.get('code')

    def __init__(self, req: HttpRequest, use_camel_case=False):
        super().__init__(req)
        self.method = req.method
        self.headers = dict(**req.headers)
        self.query = dict(**req.params)
        self.path = unquote_plus(self.BASE_PATH_RE.sub('', req.url).split('?')[0])

        try:
            self.body = req.get_json()

            if use_camel_case:
                self.body = camel_to_snake(self.body)
        except ValueError:
            self.body = req.get_body()


class Response(HttpResponse):
    def __init__(self, *args, use_camel_case=False, **kwargs):
        if 'body' in kwargs:
            args = [kwargs['body']]
            del kwargs['body']
        else:
            args = list(args)

            if not args:
                args[0] = b''

        if isinstance(args[0], (dict, Iterable)) and not isinstance(args[0], (str, bytes)):
            args[0] = json.dumps(args[0], cls=UniversalEncoder)

            if 'headers' not in kwargs:
                kwargs['headers'] = {}

            kwargs['headers']["Content-Type"] = "application/json"

        if use_camel_case and kwargs.get('headers', {}).get("Content-Type") == "application/json":
            args[0] = json.dumps(snake_to_camel(json.loads(args[0])), cls=UniversalEncoder)

        if not isinstance(args[0], bytes):
            args[0] = args[0].encode('utf-8')

        super().__init__(*args, **kwargs)

    @property
    def dict(self) -> dict:
        return {
            'statusCode': self.status_code,
            'headers': dict(self.headers),
            'body': self.get_body().decode('utf-8')
        }
