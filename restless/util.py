import json
from datetime import datetime
from typing import Iterable
import re
from collections import namedtuple

C2S1 = re.compile('(.)([A-Z][a-z]+)')
C2S2 = re.compile('([a-z0-9])([A-Z])')
S2C = re.compile('(.)_([a-zA-Z])')


def camel_to_snake(obj):
    if isinstance(obj, (list, set)):
        return [camel_to_snake(i) if not isinstance(i, str) else i for i in obj]
    elif isinstance(obj, dict):
        return {camel_to_snake(k): camel_to_snake(v) if not isinstance(v, str) else v for k, v in obj.items()}
    elif isinstance(obj, str):
        string = C2S1.sub(r'\1_\2', obj)
        return C2S2.sub(r'\1_\2', string).lower()

    return obj


def snake_to_camel(obj):
    if hasattr(obj, 'dict'):
        obj = obj.dict()

    if isinstance(obj, (list, set)):
        return [snake_to_camel(i) for i in obj]
    elif isinstance(obj, dict):
        return {
            snake_to_camel(k): snake_to_camel(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, str):
        return S2C.sub(lambda x: x[1] + x[2].upper(), obj)

    return obj


class UniversalEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'dict'):
            return obj.dict()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, str):
            return obj
        elif isinstance(obj, Iterable):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


class FormData(dict):
    LOCATION = 'formData'
    DELIMITER = re.compile(b'(--.*?)\r\n')
    FILE_RE = re.compile('name="(.*)"; filename="(.*)"\r\nContent-Type: (.*)')
    KEY_VALUE_RE = re.compile('name="(.*)"')
    File = namedtuple('File', 'name data content_type')

    def __init__(self, payload: bytes):
        super().__init__()
        boundary = self.DELIMITER.match(payload).group(1)

        data_re = re.compile(
            boundary + b'\r\nContent-Disposition: form-data; (.*?)\r\n(?=' + boundary + b')', re.DOTALL
        )

        for part in data_re.findall(payload):
            names, data = part.split(b'\r\n\r\n', 1)
            names = names.decode()

            if 'filename' in names:
                name, filename, content_type = self.FILE_RE.search(names).groups()
                self[name] = self.File(filename, data, content_type)
            else:
                name = self.KEY_VALUE_RE.match(names).group(1)
                self[name] = data.decode()
